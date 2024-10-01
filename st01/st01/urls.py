from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('about-us/', views.about, name='about'),
    path('contact-us/', views.contact, name='contact'),
    path('products/<int:id>/', views.product, name='product'),
    path('userdetails/', views.login, name='loginhome'),
    path('cart/', views.cart, name='cart'),
    path('registration/', views.signup, name='register'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('admin/', admin.site.urls),
]