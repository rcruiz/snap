"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from myfrstapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.principal),
    path('contact', views.info),
    path('analyze', views.analyze),
    path('basic', views.basic),
    path('intermediate', views.intermediate),
    path('advanced', views.advanced),
    path('login', views.login_user),
    path('type-signup', views.choose),
    path('signup', views.signup),
    path('logout', views.logout_user),
    path('projects', views.show_projects),
    path('project/<str:name>', views.show_project),
    path('dashboard', views.dashboard),
    path('dashboard/<str:tag>', views.dashboard_level),
    path('admin/', admin.site.urls),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
