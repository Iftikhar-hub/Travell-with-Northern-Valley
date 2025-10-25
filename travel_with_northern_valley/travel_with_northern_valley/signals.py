# travel_with_northern_valley/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TravelTip, ItineraryDay, ItineraryImage
from firebase_admin import db

@receiver(post_save, sender=TravelTip)
def push_travel_tip_to_firebase(sender, instance, created, **kwargs):
    if created:
        tip_ref = db.reference('travel_tips')
        tip_data = {
            'title': instance.title,
            'tenure': instance.tenure,
            'image': instance.image.url if instance.image else "",
        }
        tip_key = tip_ref.push(tip_data).key
        instance.firebase_id = tip_key
        instance.save(update_fields=['firebase_id'])

@receiver(post_save, sender=ItineraryDay)
def push_itinerary_day_to_firebase(sender, instance, created, **kwargs):
    travel_tip = instance.travel_tip
    if travel_tip.firebase_id:
        itinerary_ref = db.reference(f'travel_tips/{travel_tip.firebase_id}/itinerary')
        day_data = {
            'day_number': instance.day_number,
            'title': instance.title,
            'description': instance.description,
            'images': []
        }
        # Push day and get key to link images later
        day_key = itinerary_ref.push(day_data).key
        instance.firebase_day_id = day_key  # Save if needed later
        instance.save(update_fields=[])  # Not required unless you're storing it locally

@receiver(post_save, sender=ItineraryImage)
def push_image_to_firebase(sender, instance, created, **kwargs):
    day = instance.itinerary_day
    travel_tip = day.travel_tip
    if travel_tip.firebase_id:
        # Find day ref (assumes push order matches, or needs adjustment using keys)
        itinerary_ref = db.reference(f'travel_tips/{travel_tip.firebase_id}/itinerary')
        days_snapshot = itinerary_ref.get()
        if days_snapshot:
            for key, val in days_snapshot.items():
                if val.get('day_number') == day.day_number:
                    images_ref = db.reference(f'travel_tips/{travel_tip.firebase_id}/itinerary/{key}/images')
                    image_data = {
                        'image': instance.image.url if instance.image else "",
                        'caption': instance.caption,
                    }
                    images_ref.push(image_data)
                    break
