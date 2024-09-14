from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from datetime import date
from django.utils.timezone import now



from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is a protected view!'}
        return Response(content)
    


from .models import Technicien, Localisation
from .serializers import TechnicienLocalisationSerializer , TechnicienSerializer, LocalisationSerializer

class ActiveTechniciensLocalisationView(APIView):
    def post(self, request):
        serializer = TechnicienSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        #this is get request from the front to do the suivi, it gets all the techniciens in list by a filter (chof lt7t)
        active_techniciens = Technicien.objects.filter(is_active__in=[True])
        techniciens_data = []
        today = now().date()
        #filter by active techniciens
        for technicien in active_techniciens:
            last_location = Localisation.objects.filter(technicien=technicien, date=today).first()#this first because whatever the sent data it is a list
            #filter by the date of today
            if last_location:
                technicien_data = {
                    'user': {
                        'id': technicien.user.id,
                        'username': technicien.user.username,
                        'email': technicien.user.email,
                    },
                    'localisation': {
                        'date': last_location.date,
                        'locations': last_location.locations,
                    }
                }
                techniciens_data.append(technicien_data)

        response_data = {'Techniciens': techniciens_data}
        return Response(response_data, status=status.HTTP_200_OK)

class LocalisationView(APIView):
    def post(self, request):
        technicien_id = request.data.get('technicien')
        location_entry = {
            'latitude': request.data.get('latitude'),
            'longitude': request.data.get('longitude'),
            'timestamp': request.data.get('timestamp'),
        }
        #these are the sent data
        today = date.today()

        localisation, created = Localisation.objects.get_or_create(
            technicien_id=technicien_id,
            date=today,
            defaults={'locations': [location_entry]},
        )
        #creating in database
        #created a boolean to determine either if the "json table" already exists that is based on the technicien and date
        if not created:
            localisation.locations.append(location_entry)
            localisation.save()

        serializer = LocalisationSerializer(localisation)#serialize the data in order that the database understand it and the get view send it to frontend(chof lfo9)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)