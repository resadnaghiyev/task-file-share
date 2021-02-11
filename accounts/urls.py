from django.urls import path

from . import views


urlpatterns = [
    # checking username and email
    path("check-username/", views.CheckUsernameView.as_view()),
    path("check-email/", views.CheckEmailView.as_view()),
]
