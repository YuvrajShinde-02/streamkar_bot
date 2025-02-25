# chat/views.py
import json
import os
import time
import string
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from googletrans import Translator
from .llm_integration import fetch_llm_answer  # Your LLM integration module

# Load FAQ data from faq_data.json
FAQ_DATA_PATH = os.path.join(os.path.dirname(__file__), "faq_data.json")
with open(FAQ_DATA_PATH, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

def normalize_query(query: str) -> str:
    """Convert the query to lowercase and remove punctuation."""
    return query.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def collect_faq_answers(query: str) -> str:
    """
    Checks all FAQ entries for any keyword match using the loaded FAQ_DATA.
    Returns the combined answer if any match is found; otherwise, returns None.
    """
    q_lower = query.lower()
    matched_answers = []
    for key, data in FAQ_DATA.items():
        if any(keyword in q_lower for keyword in data["keywords"]):
            matched_answers.append(data["answer"])
    if matched_answers:
        return "\n\n".join(matched_answers)
    else:
        return None

# HTML view for rendering the form-based interface
def index(request):
    answer = None
    question = ""
    if request.method == "POST":
        question = request.POST.get('question', '')
        language = request.POST.get('language', 'en')
        
        # Out-of-domain check: If the query does not contain any relevant keywords, return fallback.
        if not any(keyword in question.lower() for key in FAQ_DATA for keyword in FAQ_DATA[key]["keywords"]):
            fallback = ("I'm sorry, I only answer questions related to StreamKar. "
                        "Please ask something relevant or contact human support for further assistance at support@streamkar.com.")
            if language != "en":
                try:
                    translator = Translator()
                    translation = translator.translate(fallback, dest=language)
                    fallback = translation.text
                except Exception as e:
                    fallback += " (Translation unavailable)"
            answer = fallback
        else:
            # In-domain processing: Try to collect FAQ answers.
            answer = collect_faq_answers(question)
            if not answer:
                answer = fetch_llm_answer(question)
        
            if language != "en":
                try:
                    translator = Translator()
                    translation = translator.translate(answer, dest=language)
                    answer = translation.text
                except Exception as e:
                    answer += " (Translation unavailable)"
    return render(request, "bot/index.html", {"question": question, "answer": answer})


# API endpoint view
# chat/views.py (API endpoint view snippet)
class ChatAPIView(APIView):
    def post(self, request, format=None):
        data = request.data
        query = data.get("query", "").strip()
        target_language = data.get("language", "en").lower()

        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Out-of-domain check: immediately return fallback for queries with no relevant keywords.
        if not any(keyword in query.lower() for key in FAQ_DATA for keyword in FAQ_DATA[key]["keywords"]):
            fallback = ("I'm sorry, I only answer questions related to StreamKar. "
                        "Please ask something relevant or contact human support for further assistance at support@streamkar.com.")
            if target_language != "en":
                try:
                    translator = Translator()
                    translation = translator.translate(fallback, dest=target_language)
                    fallback = translation.text
                except Exception as e:
                    fallback += " (Translation unavailable)"
            return Response({"answer": fallback}, status=status.HTTP_200_OK)
        
        normalized_query = normalize_query(query)
        cache_key = f"chat_response:{normalized_query}"
        cached_answer = cache.get(cache_key)
        if cached_answer:
            answer = cached_answer
        else:
            # First, attempt to get FAQ-based answer
            answer = collect_faq_answers(query)
            if not answer:
                # If FAQ matching fails, use the LLM with a timeout.
                answer = fetch_llm_answer_with_timeout(query, timeout=0.5)
            cache.set(cache_key, answer, timeout=3600)

        if target_language != "en":
            try:
                translator = Translator()
                translation = translator.translate(answer, dest=target_language)
                answer = translation.text
            except Exception as e:
                answer += " (Translation unavailable)"

        print(f"Chat log - Query: {query} | Answer: {answer}")
        return Response({"answer": answer}, status=status.HTTP_200_OK)

