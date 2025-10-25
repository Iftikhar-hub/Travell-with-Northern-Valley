from django import views
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('booking/', views.booking_page, name='booking_page'), 
    path('rate-and-fare/', views.rate_and_fare, name='rate_and_fare'),
    path('events/', views.events, name='events'),
    path('send_contact_message/', views.send_contact_message, name='send_contact_message'),
    path('tours/', views.tours_view, name='tours'),
    path('hotels/', views.hotels_view, name='hotels'),
    path('booking/<str:tip_id>/', views.booking, name='booking'),
    path('booking-now/<str:tip_id>/', views.booking_now, name='booking_now'),
    path('trip_detail/<str:firebase_id>/', views.trip_detail, name='trip_detail'),





]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

