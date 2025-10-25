from firebase_admin import db
from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    subject = models.CharField(max_length=100)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TravelTip(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='travel_tips/')
    tenure = models.CharField(max_length=200, default="1")
    firebase_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


class ItineraryDay(models.Model):
    travel_tip = models.ForeignKey(TravelTip, on_delete=models.CASCADE, related_name='itinerary_days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"{self.travel_tip.title} - Day {self.day_number}"


class ItineraryImage(models.Model):
    itinerary_day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='itinerary_images/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.itinerary_day} - {self.caption[:30]}"


