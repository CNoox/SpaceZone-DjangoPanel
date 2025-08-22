from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
import os
from .models import CustomUser, VerificationCode


class SmartEmailSerializer(serializers.Serializer):
    """
    Serializer to handle both registration and login verification code sending.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        allowed_domains = ['gmail.com', 'yahoo.com']
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise serializers.ValidationError("Email domain not allowed")
        return value

    def validate_password(self, value):
        # Always validate password (register + login)
        validate_password(value)
        return value

    def send_verification_code(self, email, password):
        user = CustomUser.objects.filter(email=email).first()

        if user:
            if user.is_verified:
                # login flow
                if not user.check_password(password):
                    raise serializers.ValidationError("Incorrect password")
                action = "login"
            elif not user.is_verified:
                user = CustomUser.objects.create_user(email=email, password=password)
                action = "register"

        else:
            # new registration
            user = CustomUser.objects.create_user(email=email, password=password)
            action = "register"

        # Generate verification code using VerificationCode model
        verification = VerificationCode.create_code_for_user(user)

        # send email
        send_mail(
            f'{action.capitalize()} Verification Code',
            f'Your verification code is: {verification.code}',
            os.getenv('EMAIL_HOST_USER'),
            [email],
            fail_silently=False,
        )
        return action


class VerifyCodeSerializer(serializers.Serializer):
    """
    Serializer for verifying the 6-digit code
    """
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get("email")
        code = data.get("code")

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")

        # Find the latest matching verification code
        verification = VerificationCode.objects.filter(
            user=user, code=code
        ).order_by("-created_at").first()

        if not verification:
            raise serializers.ValidationError("Invalid code")

        if verification.is_expired():
            raise serializers.ValidationError("Code expired")

        # If this was a registration, mark the user as verified
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        # If this was a login, you can issue a JWT token in the view
        return data


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")
        return user

    def send_verification_code(self, user, email):
        if user.is_verified:
            raise serializers.ValidationError("Account already verified")

        verification = VerificationCode.create_code_for_user(user)
        action = "verify"

        send_mail(
            f'{action.capitalize()} Verification Code',
            f'Your verification code is: {verification.code}',
            os.getenv('EMAIL_HOST_USER'),
            [email],
            fail_silently=False,
        )

        return action
