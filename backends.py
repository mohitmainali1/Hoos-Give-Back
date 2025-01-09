from django.contrib.auth.backends import ModelBackend
from communityservice.models import CustomUser

class PMABackend(ModelBackend):
    def authenticate(self, username=None, **kwargs):
        UserModel = CustomUser
        try:
            user = UserModel.objects.get(username=username)
            if user:
                return user
        except User.DoesNotExist:
            return None