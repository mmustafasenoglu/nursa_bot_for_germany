import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rag_pipeline import ask, get_conversation, clear_conversation


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "NurseMate AI Backend"}, status=status.HTTP_200_OK)


class ChatAPIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        language = request.data.get("language", "en")
        session_id = request.data.get("session_id", "default")

        if not question:
            return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = ask(question, language, session_id)
            return Response({
                "answer": answer,
                "session_id": session_id,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id", "default")
        conversation = get_conversation(session_id)
        history = []
        msgs = conversation.get_history()
        for i in range(0, len(msgs), 2):
            if i + 1 < len(msgs):
                history.append({
                    "user": msgs[i].content,
                    "bot": msgs[i + 1].content,
                })
        return Response({"history": history, "session_id": session_id})

    def delete(self, request):
        session_id = request.query_params.get("session_id", "default")
        clear_conversation(session_id)
        return Response({"message": "Chat cleared", "session_id": session_id})
