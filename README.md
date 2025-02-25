StreamKar AI Customer Support Bot
Overview
The StreamKar AI Customer Support Bot is a live chatbot built to assist users with queries related to StreamKar—a leading live streaming platform. The bot is designed to:

Answer platform-related queries (e.g., about streaming, signing up, payments, events, and technical support) using a pre-defined FAQ database.
Fallback to an LLM response (using microsoft/DialoGPT-small or a fine-tuned variant) when the FAQ does not cover the query.
Filter out-of-domain queries by immediately returning a fallback message.
Provide multi-language support using Google Translate (e.g., English, Hindi, French, Spanish, German).
Optimize performance through caching with Redis and a timeout wrapper for LLM calls.

Features
Real-Time Assistance:
Fast responses for common queries (FAQ lookup, target <300ms) and a fallback mechanism for queries not covered.
LLM Fallback:
Generates responses for non-FAQ queries, with a timeout wrapper (target <500ms on optimized hardware).
Domain Filtering:
Out-of-domain queries (e.g., “what is react”) trigger an immediate fallback message.
Multi-Language Support:
On-the-fly translation using Google Translate.
Caching:
Uses Django’s caching framework with Redis to store and quickly retrieve responses.
Performance Optimization:
Model is loaded once at startup and LLM calls are wrapped in a timeout to ensure timely responses.


Architecture
Backend Framework:
Django with Django REST Framework.
FAQ Database:
Stored in faq_data.json (loaded at startup) and used for keyword-based query matching.
LLM Integration:
Uses microsoft/DialoGPT-small (loaded via Hugging Face Transformers in llm_integration.py). A timeout wrapper is applied to optimize latency.
Multi-Language Translation:
Integrated using the googletrans library.
Caching:
Implemented with Django’s caching framework and Redis to minimize response time for repeated queries.


Repository Structure

streamkar_bot/
├── bot/
│   ├── __init__.py
│   ├── views.py                # Contains HTML and API views
│   ├── llm_integration.py      # LLM integration and timeout wrapper code
│   ├── faq_data.json           # FAQ data file
│   └── templates/
│       └── bot/
│           └── index.html      # HTML interface template
├── fine_tune_dialoGPT.py        #Fine-tuning script for DialoGPT
├── streamkar_bot/
│   ├── __init__.py
│   ├── settings.py             # Django settings; includes cache configuration
│   ├── urls.py                 # Project URL configuration
│   └── wsgi.py
├── requirements.txt            # Python dependencies list
└── README.md                   # This file


Setup and Installation
1. Clone the Repository:
    git clone <repository-url>
    cd streamkar_bot
2. Create and Activate a Virtual Environment
3. Install Dependencies:
    pip install -r requirements.txt
4. Set Up Redis:
    brew install redis
    brew services start redis
5. Fine-Tune Your LLM:
    python fine_tune_dialoGPT.py


Running the Bot
1. Apply Migrations
    python manage.py migrate
2. Start the Development Server:
    python manage.py runserver
3. Access the HTML Interface:
    Open your browser and navigate to http://127.0.0.1:8000/.
    Use the form to submit queries and select your desired language (e.g., English, Hindi, etc.).
4. Test the API Endpoint:
    Use Postman or cURL to send a POST request to:
    http://127.0.0.1:8000/api/chat/

    Example JSON payload:
    {
    "query": "What is StreamKar?",
    "language": "hi"
    }

API Documentation
Endpoint: /api/chat/
Method: POST
Request Parameters:
query (string, required): The user's query.
language (string, optional): The target language code (default: "en").
Response:
Returns a JSON object with an "answer" key containing the response.