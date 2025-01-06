from rest_framework.response import Response
from rest_framework.decorators import api_view
@api_view(['GET'])
def index(request):
    """Return a simple welcome message."""
    return Response({'message': 'Welcome to the e-commerce API!'})
