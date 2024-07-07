from django.urls import path
from .views import *
import uuid


urlpatterns = [
    path("", welcome_view, name="welcome"),
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("api/users/<uuid:userId>", GetUserView.as_view(), name= "get_user"),
    path("api/organisations", GetOrganisationView.as_view(), name="get_organisation"),
    path("api/organisations/<uuid:orgId>", GetOrganisationById.as_view(),name="get_an_organisation"),
    path("api/organisations/<uuid:orgId>/users", AddUserToOrganisation.as_view(), name="add_user"),
]
