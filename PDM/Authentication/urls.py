

from django.urls import path
from .views import *

urlpatterns = [
    path('register-account/',create_account),
    path('verify-account/<str:token>/',account_verify),
    path('login/',login_user),
    path('logout/', logout_user),


    path('makeadmin/',makeAdmin)
]
