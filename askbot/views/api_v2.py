from rest_framework.views import APIView, exception_handler
from rest_framework.response import Response
from askbot.serializers.question_search import QuestionSearchSerializer

def api_exception_handler(exc, context):
    """Exception handler for the Django Rest Framework"""
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response


class QuestionSearch(APIView):
    """Read only view for the main question search"""

    def get(self, request, format=None):
        """Returns data for the questions matching search,
        sufficient to render the main page"""
        serializer = QuestionSearchSerializer(request.data, context={'request': request})
        return Response(serializer.data)
