from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *
from django.contrib.auth import login, logout
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

def welcome_view(request):
    return HttpResponse("Welcome to the Authentication & organization API for hng!")

#Functions to handle errors
def handle_validation_error(e):
    errors = [{"field": k, "message": v} for k, v in e.detail.items()]   
    return Response({
        "errors": errors
    }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

def handle_authentication_failed(e):
    return Response({
        "status": "error",
        "message": str(e),
    }, status=status.HTTP_401_UNAUTHORIZED)

def handle_generic_error(e, message="Client error"):
    return Response({
        "status": "error",
        "message": message,
    }, status=status.HTTP_400_BAD_REQUEST)



#User registration View
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "accessToken": access_token,
                        "user": {
                            "userId": user.userId,
                            "firstName": user.firstName,
                            "lastName": user.lastName,
                            "email": user.email,
                            "phone": user.phone,
                        }
                    }
                }, status=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                return handle_validation_error(e)

            except Exception as e:
                return handle_generic_error(e, "Registration unsuccessful")



# User Login View
class LoginView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']

            user = CustomUser.objects.filter(email=email).first()

            if user is None:
                raise AuthenticationFailed("User not found")

            if not user.check_password(password):
                raise AuthenticationFailed("password is Incorrect")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            login(request, user)
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": access_token,
                    "user": {
                        "userId": user.userId,
                        "firstName": user.firstName,
                        "lastName": user.lastName,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            return handle_validation_error(e)

        except AuthenticationFailed as e:
            return handle_authentication_failed(e)

        except Exception as e:
            return handle_generic_error(e, "Authentication failed")

# API view to fetch user details by userId
class GetUserView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, userId):
        logged_user = request.user
        try:
            user = get_object_or_404(CustomUser, userId=userId)
            # Assuming the Organisation model has a field like `users` which is a ManyToManyField or ForeignKey
            user_organisations = Organisation.objects.filter(users=logged_user)

            if user_organisations.filter(users=user).exists():
                serializer = RegisterSerializer(user)
                return Response({
                    "status": "success",
                    "message": "User found",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "You do not have permission to view user data",
                }, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return handle_generic_error(e, "Client error")

# list and create organisations
class GetOrganisationView(generics.ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            organisations = request.user.organisations.all()
            data = [{
                "orgId": organisation.orgId,
                "name": organisation.name,
                "description": organisation.description,
            } for organisation in organisations]

            return Response({
                "status": "success",
                "message": "Organisations retrieved successfully",
                "data": data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_generic_error(e, "Client error")

    def post(self, request):
        try:
            serializer = OrganisationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            organisation = serializer.save()
            organisation.users.add(request.user)

            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": {
                    "orgId": organisation.orgId,
                    "name": organisation.name,
                    "description": organisation.description
                }
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return handle_validation_error(e)

        except Exception as e:
            return handle_generic_error(e, "Client error")

# API View to get details of a organisation by orgId
class GetOrganisationById(generics.GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, orgId):
        try:
            organisation = get_object_or_404(Organisation, orgId=orgId)
            serializer = OrganisationSerializer(organisation)
            return Response({
                "status": "success",
                "message": "Organisation found",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_generic_error(e, "Client error")

# API view to add a user to an organisation
class AddUserToOrganisation(generics.GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, orgId):
        data = request.data        
        try:
            organisation = get_object_or_404(Organisation, orgId=orgId)
            if request.user in organisation.users.all():
                user = get_object_or_404(User, userId=data["userId"])
                organisation.users.add(user)

                return Response({
                    "status": "success", 
                    "message": "User added to organisation successfully"
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "status": "error", 
                    "message": "You do not have permission to add user"
                }, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return handle_generic_error(e, "Client error")
