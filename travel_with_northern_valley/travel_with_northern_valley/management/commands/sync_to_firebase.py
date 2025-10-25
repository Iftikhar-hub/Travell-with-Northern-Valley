from django.core.management.base import BaseCommand
from travel_with_northern_valley.models import TravelTip
import firebase_admin
from firebase_admin import credentials, db

class Command(BaseCommand):
    help = 'Sync Travel Tips and Itineraries to Firebase Realtime Database'

    def handle(self, *args, **options):
        # Initialize Firebase only once
        if not firebase_admin._apps:
            cred = credentials.Certificate('../firebase/travel-with-northern-valley-firebase-adminsdk-fbsvc-3aa4152aa6.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://travel-with-northern-valley-default-rtdb.firebaseio.com/'
            })

        for tip in TravelTip.objects.all():
            ref = db.reference('travel_tips')
            new_tip = ref.push({
                'title': tip.title,
                'tenure': tip.tenure,
                'image': tip.image.url if tip.image else "",
            })

            tip.firebase_id = new_tip.key
            tip.save(update_fields=['firebase_id'])

            # Push itinerary days
            itinerary_ref = db.reference(f'travel_tips/{new_tip.key}/itinerary_days')
            for day in tip.itinerary_days.all():
                # Collect images for the day
                images = [
                    {
                        'image': img.image.url if img.image else "",
                        'caption': img.caption
                    }
                    for img in day.images.all()
                ]

                itinerary_ref.push({
                    'day_number': day.day_number,
                    'title': day.title,
                    'description': day.description,
                    'images': images
                })

        self.stdout.write(self.style.SUCCESS('Data successfully synced to Firebase.'))
