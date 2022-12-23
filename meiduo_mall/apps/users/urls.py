from django.urls import path
from apps.users.views import UsernameCountView,Test
urlpatterns = [
    path('usernames/<username>/count/',UsernameCountView.as_view()),
    path('users',Test.as_view())
]
