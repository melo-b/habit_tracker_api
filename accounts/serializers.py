from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Build an unsaved user so similarity checks (username/email vs password) work
        candidate = User(username=attrs.get('username'), email=attrs.get('email', ''))
        validate_password(attrs['password'], user=candidate)
        return attrs

    def create(self, validated_data):
        # Self-registered accounts are always standard users; role is never client-supplied
        return User.objects.create_user(role='user',**validated_data)
