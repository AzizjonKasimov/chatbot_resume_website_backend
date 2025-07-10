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

@csrf_exempt
@require_http_methods(["GET", "POST"])
def chat_endpoint(request):
    if request.method == "GET":
        logger.info("Starting the chat endpoint")
        user_message = request.GET.get("message", "").strip()

        # Your resume context
        resume_context = """
        Name: Azizjon
        Experience: I worked in Rex Innovation and G-Man Auto Parts as an AI Engineer.
        Skills: Quick to adapt to new circumstances and very curious by nature.
        Education: I graduated high school in Tashkent and then Woosong University in South Korea
        Projects: Done many projects
    
        Answer questions about this person's background professionally and helpfully.
        """

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