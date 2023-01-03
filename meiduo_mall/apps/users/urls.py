from django.urls import path
from apps.users.views import UsernameCountView,RegisterView,MobileCountView,LoginView,EmailView,LogoutView,CenterView
urlpatterns = [
    path('usernames/<username>/count/',UsernameCountView.as_view()),
    path('register/',RegisterView.as_view()),
    path('mobiles/<mobile>/count/',MobileCountView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('info/',CenterView.as_view()),
    path('emails/', EmailView.as_view()),
]
