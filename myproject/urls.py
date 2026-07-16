"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from core.views import home, login_view, register, delete_plan
from core.views import logout_view
from core.views import dashboard
from core.views import generate_pdf
from django.conf import settings
from django.conf.urls.static import static
from core.views import add_plan
from core.views import manage_plans
from core.views import edit_plan, plan_details

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('login/', login_view),
    path('register/', register),
    path('logout/', logout_view),
    path('dashboard/', dashboard),
    path('report/', generate_pdf),
    path('add-plan/', add_plan),
    path('manage-plans/', manage_plans),
    path('edit-plan/<int:plan_id>/', edit_plan),
    path('delete-plan/<int:plan_id>/', delete_plan),
    path('plan/<int:plan_id>/', plan_details),
]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)