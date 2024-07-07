from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('userId', 'firstName', 'lastName', 'email', 'phone')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('userId', 'firstName', 'lastName', 'email', 'phone')