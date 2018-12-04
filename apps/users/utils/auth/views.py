from rest_framework.views import APIView

from .serializers import JWTSerializer, RefreshJWTSerializer, VerificationBaseSerializer
from .settings import api_settings

from rest_framework.response import Response
from rest_framework import status

from datetime import datetime


class JWTAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_context(self):
        return {
            'request': self.request,
            'view': self
        }

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            # response_data = jwt_response_payload_handler(token, user, request)
            response_data = {'token': token}
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainJWTView(JWTAPIView):
    serializer_class = JWTSerializer


class RefreshJWTView(JWTAPIView):
    serializer_class = RefreshJWTSerializer
