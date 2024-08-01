from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet

"""
This urls.py file uses a router to automatically generate URL patterns for a ViewSet.
This approach is beneficial when you have a resource (like quizzes) that needs 
standard CRUD operations, as it reduces boilerplate code.
"""

# Create a router and register our ViewSet with it.
router = DefaultRouter()
router.register(r'', QuizViewSet, basename='quiz')

# The router.urls attribute contains all the URL patterns for our QuizViewSet.
urlpatterns = [
    path('', include(router.urls)),
]

"""
The router will create the following URL patterns:
- List: GET /api/quizzes/
- Create: POST /api/quizzes/
- Retrieve: GET /api/quizzes/{id}/
- Update: PUT /api/quizzes/{id}/
- Partial Update: PATCH /api/quizzes/{id}/
- Delete: DELETE /api/quizzes/{id}/
- Any custom actions defined in the ViewSet, e.g., GET /api/quizzes/my_quizzes/

This approach is particularly useful for RESTful APIs as it follows
conventions and reduces the amount of code needed to set up standard operations.
"""
