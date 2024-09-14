"""
URL mapping for user api endpoints.
"""

from django.urls import path

from user import views

# Used for reverse mapping
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView().as_view(), name='me')
]
