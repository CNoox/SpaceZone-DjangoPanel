from rest_framework import serializers
from .models import CustomUserModel,UserCodeModel
from password_strength import PasswordPolicy
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ['email','password']
        extra_kwargs = {
            'password': {'write_only': True,'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        return CustomUserModel.objects.create_user(email=validated_data['email'], password=validated_data['password'])

    def validate_password(self,value):
        policy = PasswordPolicy.from_names(
            length=12,
            uppercase=2,
            numbers=4,
            special=2,
        )
        error = policy.test(value)
        if error:
            raise ValidationError(f'Password is too weak: {error}')
        return value

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = CustomUserModel
        fields = ['email','password']
        extra_kwargs = {
            'password': {'write_only': True,'required': True},
            'email': {'required': True}
        }

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError("Must include email and password")


class UserPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ['email','first_name','last_name','avatar','national_code','phone_number','last_login']

class UserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCodeModel
        fields = ['code']