from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_principal, name='menu_principal'),  # ruta del menú
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/registrar/', views.registrar_ventas, name='registrar_ventas'),
]
