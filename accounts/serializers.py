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
        fields = ['id','email','first_name','last_name','avatar','national_code','phone_number','last_login','is_superuser']
        extra_kwargs = {'email':{'required':False},
                        'is_superuser': {'read_only':True},
                        'last_login':{'read_only':True}
                        }

class UserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCodeModel
        fields = ['code']

class UserVerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, write_only=True)
    def validate(self,data):
        user = CustomUserModel.objects.filter(email=data['email']).first()
        if not user or not user.usercode.verify_code(data['code']):
            raise serializers.ValidationError("Invalid or expired code")
        return data


class SendCodeForgetUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self,value):
        user = CustomUserModel.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Email is not exist.")
        self.user = user
        return value

    def save(self):
        if not self.user.usercode.can_request_new():
            remaining = self.user.usercode.seconds_until_next_code()
            raise serializers.ValidationError(f"Cannot request code yet for {remaining}.")
        code = self.user.usercode.create_code()
        return code

class UpdatePasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True,write_only=True)
    class Meta:
        model = CustomUserModel
        fields = ['password','password2']
        extra_kwargs = {'password': {'required': True, 'write_only': True},
                        'password2': {'required': True, 'write_only': True}
                        }
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

    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords is incorrect.')
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save(update_fields=['password'])
        return instance
