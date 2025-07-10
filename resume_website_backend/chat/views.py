# chat/views.py
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from google import genai
from django.conf import settings

# To log messages to the console
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This sends logs to the console/terminal
    ]
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_context():
    with open(r'resume_website_backend/chat/context.txt', 'r', encoding='utf-8') as f:
        return f.read()

@csrf_exempt
@require_http_methods(["GET", "POST"])
def chat_endpoint(request):
    # shared resume context
    context = get_context()
    resume_context = f"""
    {context}

    The above is an information about Azizjon Kasimov.
    Answer questions about this person's background professionally and helpfully. Use plain text
    when answering to the users.
    """

    # extract message depending on method
    if request.method == "GET":
        user_message = request.GET.get("message", "").strip()
    else:  # POST
        try:
            body = json.loads(request.body.decode())
            user_message = body.get("message", "").strip()
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON payload', 'status': 'error'},
                                status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty message', 'status': 'error'}, status=400)

    prompt = f"{resume_context}\n\nUser question: {user_message}\n\nProvide a helpful response about this person's background:"
    logger.info("Sending request to Gemini API")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    logger.info("Successfully generated the response.")

    return JsonResponse({
        'response': response.text,
        'status': 'success'
    })


def index(request):
    return JsonResponse({'message': 'Resume Chat API is running!'})