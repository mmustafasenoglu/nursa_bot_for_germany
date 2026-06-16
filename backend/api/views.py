from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rag_pipeline import ask

class ChatAPIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        language = request.data.get("language", "en")
        
        if not question:
            return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            answer = ask(question, language)
            return Response({"answer": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
