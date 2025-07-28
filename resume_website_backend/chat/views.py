import logging

from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from google import genai
from django.conf import settings
from google.genai import types
from django.core.cache import cache
import uuid

from resume_website_backend.chat.instructions import get_instructions

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
instructions = get_instructions()
SYSTEM = types.GenerateContentConfig(system_instruction=instructions)
CACHE_TTL = 3600  # 1 hour


def get_chat_with_history(session_id):
    key = f"history_{session_id}"
    # Load the list of dicts, defaulting to empty
    raw_history = cache.get(key, [])

    # Turn each dict back into a Content object
    content_history = [
        types.Content(**msg) for msg in raw_history
    ]

    # Create a brand-new Chat, passing in your history
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=SYSTEM,
        history=content_history
    )
    return chat, key


@csrf_exempt
@require_http_methods(["GET", "POST"])
def chat_endpoint(request):
    # Extract message and session_id depending on method
    if request.method == "GET":
        logger.info("Received GET request to chat endpoint")
        user_message = request.GET.get("message", "").strip()
        session_id = request.GET.get("session_id", "")
    else:  # POST
        try:
            logger.info("Received POST request to chat endpoint")
            body = json.loads(request.body.decode())
            user_message = body.get("message", "").strip()
            session_id = body.get("session_id", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON payload', 'status': 'error'},
                                status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty message', 'status': 'error'}, status=400)

    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        # Get or create chat for this session
        logger.info(f"Processing chat request for session {session_id} with message: {user_message}")
        chat, hist_key = get_chat_with_history(session_id)

        logger.info(f"Sending request to Gemini API for session {session_id}")
        response = chat.send_message(user_message)
        logger.info("Successfully generated the response.")

        # Build two dicts to represent the new turns
        user_entry = {"role": "user", "parts": [{"text": user_message}]}
        model_entry = response.candidates[0].content.model_dump()

        # Append to your raw_history and save
        raw_history = cache.get(hist_key, [])
        raw_history.extend([user_entry, model_entry])
        cache.set(hist_key, raw_history, CACHE_TTL)

        return JsonResponse({
            'response': response.text,
            'session_id': session_id,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return JsonResponse({
            'error': 'Failed to process chat request',
            'status': 'error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_chat(request):
    """Reset/clear chat history for a session"""
    try:
        body = json.loads(request.body.decode())
        session_id = body.get("session_id", "")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON payload', 'status': 'error'},
                            status=400)

    if not session_id:
        return JsonResponse({'error': 'Session ID required', 'status': 'error'}, status=400)

    # Clear the chat from cache
    chat_key = f"chat_{session_id}"
    cache.delete(chat_key)

    return JsonResponse({
        'message': 'Chat history reset successfully',
        'status': 'success'
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def feedback_email(request):
    data = json.loads(request.body)
    subject = f"Feedback ({data['feedback']}) Message {data['message_id']}"

    # Format the chat history
    history_lines = []
    for msg in data['history']:
        # mention the id…
        history_lines.append(f"Message ID {msg['id']}:")
        # …then sender + text, indented
        history_lines.append(f"  {msg['sender']}: {msg['text']}\n")
    # join them with newlines
    history_str = "\n".join(history_lines)
    body = (
        f"Chat history:\n\n\n"
        f"{history_str}\n\n\n"
        f"Comment: {data['comment']}\n\n"
    )

    try:
        send_mail(
            subject,
            body,
            'azizkhasimov@gmail.com',
            ['azizkhasimov@gmail.com'],
            fail_silently=False
        )
        return JsonResponse({'status': 'sent'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def index(request):
    return JsonResponse({'message': 'Resume Chat API is running!'})