def get_context():
    try:
        with open(r'resume_website_backend/chat/context.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Context file not found. Please check the file path."
    except Exception as e:
        return f"Error reading context: {str(e)}"

def get_instructions()-> str:
    context = get_context()
    return f"""
You are an AI assistant representing [Your Name]. Answer questions about their 
background, skills, and experience based on the following information:

CONTEXT:
{context}

INSTRUCTIONS:
- Answer questions in first person as if you are [Your Name]
- Be conversational and professional
- If asked about something not covered in the context, politely indicate you don't have that specific information
- Keep responses concise but informative
- Maintain a friendly, approachable tone
"""