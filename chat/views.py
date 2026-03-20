from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import run_agent_with_history

def index(request):
    # Clear memory when page loads fresh
    if 'history' not in request.session:
        request.session['history'] = []
    return render(request, 'chat/index.html')

@csrf_exempt
def ask(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        if not user_message:
            return JsonResponse({'error': 'No message'}, status=400)
        try:
            # Get conversation history from session
            history = request.session.get('history', [])

            answer, updated_history = run_agent_with_history(user_message, history)

            # Save updated history back to session
            request.session['history'] = updated_history
            request.session.modified = True

            return JsonResponse({'response': answer})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST only'}, status=405)

@csrf_exempt
def clear_history(request):
    """Clear conversation memory"""
    if request.method == 'POST':
        request.session['history'] = []
        request.session.modified = True
        return JsonResponse({'status': 'cleared'})
    return JsonResponse({'error': 'POST only'}, status=405)