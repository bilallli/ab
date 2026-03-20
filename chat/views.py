from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import run_agent_with_history
from vision import analyze_image
from pdf_handler import (
    extract_text_from_pdf,
    summarize_pdf,
    answer_pdf_question,
    analyze_scanned_pdf
)


def index(request):
    if 'history' not in request.session:
        request.session['history'] = []
    return render(request, 'chat/index.html')


@csrf_exempt
def ask(request):
    if request.method == 'POST':

        # ── Handle PDF upload ─────────────────────────────────
        if request.FILES.get('pdf'):
            pdf_file = request.FILES['pdf']
            question = request.POST.get('message', '').strip()
            filename = pdf_file.name
            pdf_bytes = pdf_file.read()

            # Try text extraction first
            extracted_text = extract_text_from_pdf(pdf_bytes)

            if extracted_text:
                # Text-based PDF — use normal summarization
                print(f"[PDF] Text-based PDF detected: {filename}")
                request.session['pdf_text'] = extracted_text
                request.session['pdf_name'] = filename
                request.session.modified = True

                if question and question.lower() not in ['summarize', 'summary']:
                    answer = answer_pdf_question(extracted_text, question, filename)
                else:
                    answer = summarize_pdf(extracted_text, filename)
            else:
                # Scanned PDF — use Groq Vision to read it as image
                print(f"[PDF] Scanned PDF detected — using Vision: {filename}")
                vision_question = question if question else (
                    "Extract and list ALL information visible in this document. "
                    "Include all text, numbers, dates, names, and any other details you can see."
                )
                answer = analyze_scanned_pdf(pdf_bytes, vision_question, filename)

                # Store extracted content for follow-up questions
                request.session['pdf_text'] = answer
                request.session['pdf_name'] = filename
                request.session.modified = True

            # Save to history
            history = request.session.get('history', [])
            history.append({
                "role": "user",
                "content": f"[PDF uploaded: {filename}] {question or 'Extract all information'}"
            })
            history.append({"role": "assistant", "content": answer})
            request.session['history'] = history
            request.session.modified = True

            return JsonResponse({'response': answer})

        # ── Handle image upload ───────────────────────────────
        if request.FILES.get('image'):
            image_file = request.FILES['image']
            question = request.POST.get('message', 'What is in this image? Describe everything in detail.')
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            media_type = image_file.content_type

            try:
                answer = analyze_image(image_data, media_type, question)
                history = request.session.get('history', [])
                history.append({
                    "role": "user",
                    "content": f"[Image uploaded] {question}"
                })
                history.append({"role": "assistant", "content": answer})
                request.session['history'] = history
                request.session.modified = True
                return JsonResponse({'response': answer})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        # ── Handle text message ───────────────────────────────
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Check if user is asking about an already uploaded PDF
        pdf_text = request.session.get('pdf_text', '')
        pdf_name = request.session.get('pdf_name', '')

        pdf_keywords = [
            'pdf', 'document', 'file', 'page', 'summarize', 'summary',
            'explain', 'what does', 'tell me about', 'find', 'extract',
            'information', 'details', 'content', 'passport', 'report'
        ]

        if pdf_text and any(word in user_message.lower() for word in pdf_keywords):
            print(f"[PDF Follow-up] Answering question about: {pdf_name}")
            answer = answer_pdf_question(pdf_text, user_message, pdf_name)
            history = request.session.get('history', [])
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": answer})
            request.session['history'] = history
            request.session.modified = True
            return JsonResponse({'response': answer})

        # Normal agent response with web search, weather, etc.
        try:
            history = request.session.get('history', [])
            answer, updated_history = run_agent_with_history(user_message, history)
            request.session['history'] = updated_history
            request.session.modified = True
            return JsonResponse({'response': answer})
        except Exception as e:
            print(f"[Agent Error] {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST only'}, status=405)


@csrf_exempt
def clear_history(request):
    if request.method == 'POST':
        request.session['history'] = []
        request.session['pdf_text'] = ''
        request.session['pdf_name'] = ''
        request.session.modified = True
        return JsonResponse({'status': 'cleared'})
    return JsonResponse({'error': 'POST only'}, status=405)