# Chatbot Resume Website - Backend

This repository contains the backend API for the [Chatbot Resume Website](https://opensourcedesign.net/) project, built with Django and Django REST Framework.

## Features

- **Chatbot Integration**: Powered by Groq's `llama-3.3-70b-versatile` model for intelligent resume interactions
- **User Feedback System**: Collects and emails user feedback directly to administrators
- **RESTful API**: Clean, well-structured endpoints to support the frontend application
- **Lightweight Database**: Uses SQLite for simplicity (no external database required)

## Tech Stack

- **Framework**: Django with Django REST Framework
- **AI Integration**: Groq API (`llama-3.3-70b-versatile`)
- **Database**: SQLite
- **Hosting**: Render (build.sh included)
- **Python Version**: 3.13 (earlier versions should work)

## Setup & Configuration

### Environment Variables

Create a `.env` file in the root directory with the following configuration:

```env
# Chat AI Configuration
CHAT_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Django Configuration
SECRET_KEY=your_django_secret_key_here

# Email Configuration (for user feedback)
EMAIL_HOST=your_email_host
EMAIL_PORT=your_email_port
EMAIL_HOST_USER=your_email_host_user
EMAIL_HOST_PASSWORD=your_email_host_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
```

### Getting API Keys

- **Groq API**: Create a server-side API key in the [Groq Console](https://console.groq.com/keys). This project uses `llama-3.3-70b-versatile` only, with a static fallback when the free-tier quota is reached or the provider is temporarily unavailable.
- **Django Secret Key**: Generate one using Django's built-in utility or online generators

### Email Configuration Notes

The email settings are used to send user feedback directly to your inbox. Configure these based on your email provider:
- **Gmail**: Use `smtp.gmail.com` with port `587` and `EMAIL_USE_TLS=True`
- **Outlook**: Use `smtp-mail.outlook.com` with port `587` and `EMAIL_USE_TLS=True`

## Deployment

This project is configured for deployment on Render with the included `build.sh` script. Set `CHAT_PROVIDER=groq`, `GROQ_MODEL=llama-3.3-70b-versatile`, and `GROQ_API_KEY` in Render's environment settings. The setup requires no external database management, making deployment straightforward.

## Customization

### Resume Context Configuration

The chatbot requires your personal information to provide accurate responses about your background:

- **Context File**: Edit `resume_website_backend/chat/context.txt` to include your work experience, skills, education, and other relevant information
- **Instructions**: Modify `resume_website_backend/chat/instructions.py` to customize how the chatbot responds and behaves

These files serve as the knowledge base for the AI, so make sure to update them with your specific details before deployment.

## Development

The backend provides API endpoints that seamlessly integrate with the frontend to deliver an interactive resume experience powered by AI. If the Groq free-tier limit is reached, the chat endpoint returns a helpful fallback response instead of failing the site.
