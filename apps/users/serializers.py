from rest_framework.reverse import reverse
from rest_framework import serializers

from .models import UserProfile, SSRAccount


class RegisterSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    ssr = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'date_joined', 'email', 'nick_name', 'birthday', 'gender',
                  'address', 'mobile', 'profile_photo', 'coin_nums', 'experience', 'level', 'ssr',)

    def get_ssr(self, row):
        return reverse(viewname='users:ssr', request=self.context['request'])

    def get_level(self, row):
        return row.user_level()


class SSRAccountSerializer(serializers.ModelSerializer):
    ss_qrcode = serializers.SerializerMethodField()
    ss_url = serializers.SerializerMethodField()
    ssr_qrcode = serializers.SerializerMethodField()
    ssr_url = serializers.SerializerMethodField()
    class Meta:
        model = SSRAccount
        fields = ('expiration_time', 'ss_qrcode', 'ss_url', 'ssr_qrcode', 'ssr_url')

    def get_ss_qrcode(self, row):
        return row.ss_qrcode

    def get_ssr_qrcode(self, row):
        return row.ssr_qrcode

    def get_ss_url(self, row):
        return row.ss_url

    def get_ssr_url(self, row):
        return row.ssr_url


class ProfilePhotoSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(max_length=None, use_url=True,)

    class Meta:
        model = UserProfile
        fields = ('profile_photo', )
