from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone_number', 
                 'user_type', 'is_verified', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'is_verified')

    def validate_email(self, value):
        request = self.context.get('request')
    
        if request and request.user and request.user.is_authenticated:
        # For existing users (updating profile)
            if User.objects.filter(email=value).exclude(id=request.user.id).exists():
                raise serializers.ValidationError("This email address is already in use.")
        else:
        # For new users (signing up)
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("This email address is already in use.")
    
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user