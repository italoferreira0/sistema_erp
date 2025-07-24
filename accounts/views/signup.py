from accounts.views.base import Base

from accounts.auth import Authentication
from accounts.serializer import UserSerializer

from rest_framework.response import Response

class Signup(Base):
    def post(self, resquest):
        name = resquest.data.get('name')
        email = resquest.data.get('email')
        password = resquest.data.get('password')

        user = Authentication.signup(self, name=name, email=email, password=password)
        serializer = UserSerializer(user)

        return Response({'user':serializer.data})
