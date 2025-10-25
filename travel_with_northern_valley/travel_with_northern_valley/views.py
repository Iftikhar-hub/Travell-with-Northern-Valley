import os
import uuid
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib import messages  # Import the messages framework
from .models import Contact
from django.core.mail import send_mail
from firebase_admin import db 
from django.shortcuts import render, get_object_or_404
import travel_with_northern_valley.firebase_config
from .models import TravelTip
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
import io
from django.views.decorators.csrf import csrf_exempt

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from datetime import datetime





# View for the About Us page
def about(request):
    return render(request, 'about.html')


def send_contact_message(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            Contact.objects.create(
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                email=form.cleaned_data['email']
            )
            
            return HttpResponseRedirect('/contact/')  # Redirect after successful submission
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


# View for the Contact Us page

# View for the Booking for specific trips
def booking(request, tip_id):
    tip_ref = db.reference(f"travel_tips/{tip_id}")
    tip_data = tip_ref.get()

    itinerary = tip_data.get("itinerary", {})
    itinerary_days = []

    for day_key, day_val in itinerary.items():
        # Convert images dict to list
        images_dict = day_val.get("images", {})
        images = list(images_dict.values())  # <-- this is important

        day_data = {
            "day_number": day_val.get("day_number"),
            "title": day_val.get("title"),
            "description": day_val.get("description"),
            "images": images,  # now it's a list!
        }

        itinerary_days.append(day_data)

    context = {
        "tip_title": tip_data.get("title"),
        "tip_tenure": tip_data.get("tenure"),
        "tip_image": tip_data.get("image"),
        "itinerary_days": sorted(itinerary_days, key=lambda x: x["day_number"]),
    }

    return render(request, "booking.html", context)

# View for the Booking for navbar
def booking_page(request):
    tips_ref = db.reference("travel_tips")
    tips_data = tips_ref.get()

    travel_tips = []
    if tips_data:
        for tip_id, tip in tips_data.items():
            travel_tips.append({
                "id": tip_id,
                "title": tip.get("title"),
                "tenure": tip.get("tenure"),
                "image": tip.get("image"),
            })

    context = {
        "travel_tips": travel_tips
    }
    return render(request, "booking.html", context)

def generate_invoice_pdf(data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    styles = getSampleStyleSheet()
    red_color = colors.HexColor("#d13d34")

    # Header background
    p.setFillColor(red_color)
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)

    # Company logo
    logo_path = "static/images/logo.png"
    try:
        logo = ImageReader(logo_path)
        p.drawImage(logo, 30, height - 90, width=60, height=60, mask='auto')
    except:
        pass  # handle missing logo gracefully

    # Company Name and Info
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.white)
    p.drawString(100, height - 50, "Travel with Northern Valley")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 65, "Location: Skardu")
    p.drawString(100, height - 78, "WhatsApp: 03474738822  |  Email: travellwithnorthernvalley@gmail.com")

    # Invoice metadata
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    p.drawString(450, height - 50, f"INVOICE NO: {data['booking_id']}")
    p.drawString(450, height - 65, f"INVOICE DATE: {datetime.now().strftime('%Y-%m-%d')}")
    p.drawString(450, height - 80, "DUE DATE: ")

   # Prepare billed info data in a table format
    billed_info_data = [
        ["BILLED TO", ""],  # Header row with merged cell style below
        ["Full Name:", data.get('full_name', '')],
        ["CNIC/Passport:", data.get('cnic', '')],
        ["City, Country, Zip:", f"{data.get('city', '')}, {data.get('country', '')}, {data.get('zip_code', '')}    "],
        ["Email:", data.get('email', '')],
        ["Payment Method:", data.get('payment_method', '')],
    ]

    
    # Create table - 2 columns: Label and Value
    billed_info_table = Table(billed_info_data, colWidths=[120, 300], hAlign='LEFT')
    

    # Style the table
    billed_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), red_color),   # Header background red
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), # Header text white
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
    
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),

        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Align first column to right
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),   # Align second column to left
    
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    # Draw the table on canvas (adjust position as needed)
    billed_info_table.wrapOn(p, width, height)
    billed_info_table.drawOn(p, 30, height - 260)

        # Spacer for table
    # p.translate(0, -220)

    # Booking Table
    item_data = [
        ["ITEM NO.", "PRODUCT/SERVICE", "QUANTITY", "UNIT PRICE", "TOTAL"],
        ["001", "Trip Booking", "1", "", ""],
    ]
    table = Table(item_data, colWidths=[60, 200, 70, 90, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), red_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 460)

    # Footer Totals
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.black)
    p.drawString(400, height - 480, "SUBTOTAL:")
    p.drawString(500, height - 480, "")
    p.drawString(400, height - 495, "DISCOUNT:")
    p.drawString(500, height - 495, "")
    p.drawString(400, height - 510, "TAX:")
    p.drawString(500, height - 510, "")

    p.setFillColor(red_color)
    p.rect(400, height - 540, 160, 20, fill=1)
    p.setFillColor(colors.white)
    p.drawString(410, height - 535, "AMOUNT DUE:")
    p.drawString(510, height - 535, "")

    # Footer Contact Info
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    p.drawString(30, 50, "Make all checks payable to Travel with Northern Valley")
    p.drawString(30, 35, "If you have any questions about this invoice, contact us at 03474738822 or travellwithnorthernvalley@gmail.com")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def booking_now(request, tip_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tip_ref = db.reference(f"travel_tips/{tip_id}")
        tip_data = tip_ref.get()

        if not tip_data:
            return JsonResponse({"success": False, "error": "Invalid travel tip ID"}, status=400)
        try:
            payment_method = request.POST.get("payment_method")
            online_option = request.POST.get("online_option") if payment_method == "Online" else "Cash"

            booking_id = str(uuid.uuid4())[:8]

            data = {
                "booking_id": booking_id,  # This should be defined earlier, such as a UUID or auto-generated ID
                "full_name": request.POST.get("full_name"),
                "cnic": request.POST.get("cnic"),
                "gender": request.POST.get("gender"),
                "country": request.POST.get("country"),
                "city": request.POST.get("city"),
                "zip_code": request.POST.get("zip_code"),
                "email": request.POST.get("email"),
    
                # Optional fields (not used in current PDF template but may be useful)
                "tip_id": tip_id,
                "payment_method": payment_method,
                "payment_detail": online_option,
                
            }

            booking_ref = db.reference("bookings").push(data)
            booking_id = booking_ref.key
            data["booking_id"] = booking_id

            pdf_buffer = generate_invoice_pdf(data)

            email = EmailMessage(
                subject='Booking Invoice',
                body='Thank you for your booking. Please find attached your invoice.',
                from_email='iftikharifti1673@gmail.com',
                to=[data["email"]],
            )
            email.attach(f'Invoice_{booking_id}.pdf', pdf_buffer.read(), 'application/pdf')
            email.send()

            return JsonResponse({"success": True, "booking_id": booking_id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# View for the Rate and Fare page
def rate_and_fare(request):
    return render(request, 'rate_and_fare.html')

# View for the Events page
def events(request):
    return render(request, 'events.html')
def tours_view(request):
    return render(request, 'tours.html')
def hotels_view(request):
    return render(request, 'tours.html')


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = {
                'subject': form.cleaned_data['subject'],
                'message': form.cleaned_data['message'],
                'email': form.cleaned_data['email'],
            }

            # Save to Firebase
            ref = db.reference('contact_messages')
            ref.push(data)

            # Optional: Save to local DB
            Contact.objects.create(**data)

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})



# View for the Home page
def home(request):
    ref = db.reference('travel_tips')
    tips_data = ref.get()

    tips = []
    if tips_data:
        for key, value in tips_data.items():
            tips.append({
                'id': key,  # Add this line
                'title': value.get('title'),
                'tenure': value.get('tenure'),
                'image': value.get('image'),
            })

    return render(request, 'home.html', {'tips': tips})



def trip_detail(request, firebase_id):
    ref = db.reference(f'travel_tips/{firebase_id}')
    tip = ref.get()

    itinerary_days = []
    if tip and 'itinerary' in tip:
        for day in tip['itinerary'].values():
            itinerary_days.append(day)
        itinerary_days.sort(key=lambda x: x['day_number'])

    return render(request, 'booking.html', {
        'tip': tip,
        'itinerary_days': itinerary_days,
    })

