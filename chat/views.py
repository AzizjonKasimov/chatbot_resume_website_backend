# chat/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')

        # Your resume context
        resume_context = """
        Name: Your Name
        Experience: Your work experience...
        Skills: Your skills...
        Education: Your education...
        Projects: Your projects...

        Answer questions about this person's background professionally and helpfully.
        """

        prompt = f"{resume_context}\n\nUser question: {user_message}\n\nProvide a helpful response about this person's background:"

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        return JsonResponse({
            'response': response.text,
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


def index(request):
    return JsonResponse({'message': 'Resume Chat API is running!'})