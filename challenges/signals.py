import secrets
import string
from io import BytesIO
from django.urls import reverse
from django.core.files.base import ContentFile
import qrcode
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Challenge

@receiver(post_save, sender=Challenge)
def update_qr(sender, instance, created, **kwargs):
    if created and instance.isQR:
        # Generate a secret QR value.
        qr_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80))
        instance.qrvalue = qr_secret
        
        base_url = 'down2earth.eu.pythonanywhere.com'
        qr_url = f"{base_url}{reverse('scan_challenge', args=[instance.challengeId, qr_secret])}"
        qr = qrcode.make(qr_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        
        # Save the QR image file without immediately saving the instance again.
        instance.QRImage.save(f"Cqr_{instance.challengeId}.png", ContentFile(buffer.getvalue()), save=False)
        instance.save()
