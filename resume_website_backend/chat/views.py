import hashlib
import json
import logging
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from resume_website_backend.chat.instructions import get_instructions

logger = logging.getLogger(__name__)

ALLOWED_HISTORY_ROLES = {"user", "assistant"}


class ChatProviderError(Exception):
    def __init__(self, reason, original=None):
        super().__init__(reason)
        self.reason = reason
        self.original = original


def get_chat_setting(name, default):
    return getattr(settings, name, default)


def get_history_key(session_id):
    return f"history_{session_id}"


def normalize_history(raw_history):
    history = []
    for message in raw_history or []:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content")
        if role in ALLOWED_HISTORY_ROLES and isinstance(content, str) and content.strip():
            history.append({"role": role, "content": content})
    return trim_history(history)


def trim_history(history):
    max_turns = get_chat_setting("CHAT_MAX_HISTORY_TURNS", 8)
    max_messages = max(1, max_turns * 2)
    return history[-max_messages:]


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def is_rate_limited(request, session_id):
    window = get_chat_setting("CHAT_RATE_LIMIT_WINDOW", 60)
    max_requests = get_chat_setting("CHAT_RATE_LIMIT_MAX_REQUESTS", 10)
    identity = f"{get_client_ip(request)}:{session_id}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    key = f"chat_rate_{digest}"

    if cache.add(key, 1, timeout=window):
        return False

    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window)
        return False

    return count > max_requests


def get_provider_reason(error):
    status_code = getattr(error, "status_code", None)
    response = getattr(error, "response", None)
    if status_code is None and response is not None:
        status_code = getattr(response, "status_code", None)

    error_name = error.__class__.__name__
    if status_code == 429 or error_name == "RateLimitError":
        return "quota_reached"
    if status_code in {401, 403} or error_name in {"AuthenticationError", "PermissionDeniedError"}:
        return "not_configured"
    return "provider_unavailable"


def generate_groq_response(messages):
    if get_chat_setting("CHAT_PROVIDER", "groq") != "groq":
        raise ChatProviderError("not_configured")

    api_key = get_chat_setting("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ChatProviderError("not_configured")

    try:
        from groq import Groq
    except ImportError as exc:
        raise ChatProviderError("provider_unavailable", exc) from exc

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=get_chat_setting("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=0.4,
            max_tokens=600,
        )
        content = completion.choices[0].message.content
    except Exception as exc:
        raise ChatProviderError(get_provider_reason(exc), exc) from exc

    if not content or not content.strip():
        raise ChatProviderError("provider_unavailable")

    return content.strip()


def build_messages(history, user_message):
    return [
        {"role": "system", "content": get_instructions()},
        *trim_history(history),
        {"role": "user", "content": user_message},
    ]


def fallback_message(reason):
    if reason == "quota_reached":
        intro = "The live AI chat limit is currently reached, so I can't generate a fresh answer right now."
    elif reason == "not_configured":
        intro = "The live AI chat is not configured yet, so I can't generate a fresh answer right now."
    else:
        intro = "The live AI chat is temporarily unavailable, so I can't generate a fresh answer right now."

    return (
        f"{intro}\n\n"
        "In the meantime, here is the quick version: I am Azizjon Kasimov, an AI/ML engineer in "
        "Daejeon, South Korea, focused on production AI systems, semantic search, MLOps, time-series "
        "modeling, backend APIs, and data/ML pipelines.\n\n"
        "Good topics to ask about once the chat is available again include my G-Man Auto Parts semantic "
        "search work, Rex Innovation solar forecasting and MLOps work, anomaly detection projects, "
        "computer vision projects, technical skills, education, and certifications.\n\n"
        "You can also reach me at azizkhasimov@gmail.com or LinkedIn: "
        "https://www.linkedin.com/in/azizjon-kasimov"
    )


def fallback_response(session_id, reason):
    return JsonResponse({
        "response": fallback_message(reason),
        "session_id": session_id,
        "status": "fallback",
        "reason": reason,
    })


def parse_chat_request(request):
    if request.method == "GET":
        return request.GET.get("message", "").strip(), request.GET.get("session_id", "")

    try:
        body = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, None

    return body.get("message", "").strip(), body.get("session_id", "")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def chat_endpoint(request):
    user_message, session_id = parse_chat_request(request)
    if user_message is None:
        return JsonResponse({"error": "Invalid JSON payload", "status": "error"}, status=400)

    if not user_message:
        return JsonResponse({"error": "Empty message", "status": "error"}, status=400)

    max_length = get_chat_setting("CHAT_MAX_MESSAGE_LENGTH", 1200)
    if len(user_message) > max_length:
        return JsonResponse({
            "error": f"Message is too long. Please keep it under {max_length} characters.",
            "status": "error",
        }, status=400)

    if not session_id:
        session_id = str(uuid.uuid4())

    if is_rate_limited(request, session_id):
        logger.warning("Chat rate limit reached for session %s", session_id)
        return fallback_response(session_id, "quota_reached")

    history_key = get_history_key(session_id)
    history = normalize_history(cache.get(history_key, []))

    try:
        logger.info("Processing Groq chat request for session %s", session_id)
        response_text = generate_groq_response(build_messages(history, user_message))
    except ChatProviderError as exc:
        logger.warning("Chat provider fallback for session %s: %s", session_id, exc.reason)
        return fallback_response(session_id, exc.reason)
    except Exception:
        logger.exception("Unexpected error in chat endpoint")
        return JsonResponse({
            "error": "Failed to process chat request",
            "status": "error",
        }, status=500)

    updated_history = trim_history([
        *history,
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response_text},
    ])
    cache.set(history_key, updated_history, get_chat_setting("CHAT_CACHE_TTL", 3600))

    return JsonResponse({
        "response": response_text,
        "session_id": session_id,
        "status": "success",
    })


@csrf_exempt
@require_http_methods(["POST"])
def reset_chat(request):
    """Reset/clear chat history for a session."""
    try:
        body = json.loads(request.body.decode())
        session_id = body.get("session_id", "")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload", "status": "error"}, status=400)

    if not session_id:
        return JsonResponse({"error": "Session ID required", "status": "error"}, status=400)

    cache.delete(get_history_key(session_id))

    return JsonResponse({
        "message": "Chat history reset successfully",
        "status": "success",
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def feedback_email(request):
    data = json.loads(request.body)
    subject = f"Feedback ({data['feedback']}) Message {data['message_id']}"

    history_lines = []
    for msg in data["history"]:
        history_lines.append(f"Message ID {msg['id']}:")
        history_lines.append(f"  {msg['sender']}: {msg['text']}\n")

    history_str = "\n".join(history_lines)
    body = (
        "Chat history:\n\n\n"
        f"{history_str}\n\n\n"
        f"Comment: {data['comment']}\n\n"
    )

    try:
        send_mail(
            subject,
            body,
            "azizkhasimov@gmail.com",
            ["azizkhasimov@gmail.com"],
            fail_silently=False,
        )
        return JsonResponse({"status": "sent"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def index(request):
    return JsonResponse({"message": "Resume Chat API is running!"})
