from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from passes.models import Pass
import csv
import qrcode

class Command(BaseCommand):
    help = "Book Passes"

    def handle(self, *args, **kwargs):
        with open('passes\management\commands\yo.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                user_id = row[0]
                slot_id = 17
                pass_instance = Pass.objects.create(userId=user_id, slotId=slot_id)
                code = pass_instance.code
                
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(code)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Save QR code with user_id as name
                img.save(f'passes/qr/{user_id}.png')
