from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView , ActiveTechniciensLocalisationView ,TokenRefreshView, LocalisationView
from .views import ProtectedView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('api/active-techniciens-localisation/', ActiveTechniciensLocalisationView.as_view(), name='active_techniciens_localisation'),
    path('api/techniciens/', ActiveTechniciensLocalisationView .as_view(), name='create_technicien'),
    path('api/localisations/', LocalisationView.as_view(), name='create_localisation')
]
