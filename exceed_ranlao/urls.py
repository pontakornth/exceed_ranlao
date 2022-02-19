"""exceed_ranlao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
import ranlao.views
from ranlao import views
from rest_framework.authtoken import views as token_views

from ranlao.middlewares import CustomAuthToken

router = routers.DefaultRouter()
router.register(r'table', views.TableViewSet)
router.register(r'log', views.LogViewSets)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('call/<int:table_number>', views.call_staff, name='call_staff'),
    path('complete/<int:table_number>', views.complete_order, name='complete_order'),
    path('api-auth-token/', CustomAuthToken.as_view(), name='get_token'),
    path('enter/', views.customer_enter, name='enter'),
    path('leave/', views.customer_leave, name='leave'),
    path('count/', views.get_current_customers, name='count'),
    path('stat/', views.get_statistic, name='statistic'),
    path('user-status/', views.get_user_status, name='user_status'),
    path('admin/', admin.site.urls, name='admin'),
]
