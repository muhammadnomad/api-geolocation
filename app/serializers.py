from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'name')
        extra_kwargs = {
            'name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    #serializer create object through ORM
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            #authentificate built-in function checks if the username and pwd are in database 
            if not user:
                raise serializers.ValidationError('Invalid username/password.')

        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        attrs['user'] = user
        return attrs
    



from .models import Technicien, Localisation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class LocationEntrySerializer(serializers.Serializer):
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    timestamp = serializers.DateTimeField()

class LocalisationSerializer(serializers.ModelSerializer):
    locations = LocationEntrySerializer(many=True)

    class Meta:
        model = Localisation
        fields = ['technicien', 'date', 'locations']
    #this serializer serialize the data to send it by the view to frontend web

class TechnicienLocalisationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    localisation = serializers.SerializerMethodField()

    class Meta:
        model = Technicien
        fields = ['user', 'localisation']

    def get_localisation(self, obj):
        last_location = Localisation.objects.filter(technicien=obj).order_by('-date').first()
        return LocalisationSerializer(last_location).data if last_location else None
    

class TechnicienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technicien
        fields = ['user', 'is_active']