"""kaax URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from kaax_app.views import entrenamiento_csv, entrenamiento_json, verificar_transaccion, verificar_multiple, reporte_excel, reporte_datos, reporte_unico, reporte_rango

# from .controllers.transacciones import revisar

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("transaction/", admin.site.urls),
    path('entrenamiento/csv/', entrenamiento_csv, name='entrenamiento_csv'),
    path('entrenamiento/json/', entrenamiento_json, name='entrenamiento_json'),
    path('verificar/individual/', verificar_transaccion, name='verificar_transaccion'),
    path('verificar/multiple/', verificar_multiple, name='verificar_multiple'),
    path('reporte/excel/', reporte_excel, name='reporte_excel'),
    path('reporte/datos/', reporte_datos, name='reporte_datos'),
    path('reporte/unico/<str:token>/<int:id>/', reporte_unico, name='reporte_unico'),
    path('reporte/rango/<str:token>/<int:inicio_id>/<int:fin_id>/', reporte_rango, name='reporte_rango'),
    
]
