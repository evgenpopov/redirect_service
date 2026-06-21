from django.urls import path

from .views import PrivateRedirectView, PublicRedirectView

urlpatterns = [
    path("redirect/public/<str:redirect_identifier>/", PublicRedirectView.as_view()),
    path("redirect/private/<str:redirect_identifier>/", PrivateRedirectView.as_view()),
]
