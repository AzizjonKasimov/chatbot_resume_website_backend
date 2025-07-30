# Chatbot Resume Website - Backend

This repository contains the backend API for the [Chatbot Resume Website](https://github.com/AzizjonKasimov/AzizjonKasimov.github.io) 
project, built with Django and Django REST Framework.

## Features

- **Chatbot Integration**: Powered by Google's Gemini API for intelligent resume interactions
- **User Feedback System**: Collects and emails user feedback directly to administrators
- **RESTful API**: Clean, well-structured endpoints to support the frontend application
- **Lightweight Database**: Uses SQLite for simplicity (no external database required)

## Tech Stack

- **Framework**: Django with Django REST Framework
- **AI Integration**: Google Gemini API
- **Database**: SQLite
- **Hosting**: Render (build.sh included)
- **Python Version**: 3.13 (earlier versions should work)

## Setup & Configuration

### Environment Variables

Create a `.env` file in the root directory with the following configuration:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

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

- **Gemini API**: Visit [Google AI Studio](https://makersuite.google.com/) to get your free API key. The Gemini API offers a generous free tier perfect for development and testing.
- **Django Secret Key**: Generate one using Django's built-in utility or online generators

### Email Configuration Notes

The email settings are used to send user feedback directly to your inbox. Configure these based on your email provider:
- **Gmail**: Use `smtp.gmail.com` with port `587` and `EMAIL_USE_TLS=True`
- **Outlook**: Use `smtp-mail.outlook.com` with port `587` and `EMAIL_USE_TLS=True`

## Deployment

This project is configured for deployment on Render with the included `build.sh` script. The setup requires no external database management, making deployment straightforward.

## Development

The backend provides API endpoints that seamlessly integrate with the frontend to deliver an interactive resume experience powered by AI.