from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager): 
    def __init__(self) -> None:
        super().__init__()