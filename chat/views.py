from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import run_agent_with_history

def index(request):
    if 'history' not in request.session:
        request.session['history'] = []
    return render(request, 'chat/index.html')


@csrf_exempt
def ask(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Normal agent response
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
        request.session.modified = True
        return JsonResponse({'status': 'cleared'})
    return JsonResponse({'error': 'POST only'}, status=405)