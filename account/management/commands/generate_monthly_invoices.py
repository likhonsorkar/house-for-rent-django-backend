import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from account.models import Invoice
from rentals.models import HouseAdvertisement, RentRequest

class Command(BaseCommand):
    help = 'Generates monthly invoices for booked house advertisements.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting monthly invoice generation...")
        
        today = timezone.localdate()
        current_month = today.month
        current_year = today.year

        monthly_advertisements = HouseAdvertisement.objects.filter(
            is_booked=True,
            bill_time=HouseAdvertisement.MONTHLY
        )

        # Pre-fetch all accepted rent requests for relevant advertisements
        # Create a dictionary mapping advertisement ID to the accepted rent request (and tenant)
        accepted_rent_requests_map = {
            rr.advertisement_id: rr
            for rr in RentRequest.objects.filter(
                advertisement__in=monthly_advertisements,
                is_accepted=True
            ).select_related('user') # Select related user to avoid another query later
        }

        for ad in monthly_advertisements:
            try:
                # Use the pre-fetched data
                accepted_rent_request = accepted_rent_requests_map[ad.id]
                tenant = accepted_rent_request.user
            except KeyError: # Use KeyError since we're accessing a dict
                self.stderr.write(self.style.WARNING(
                    f"Skipping Ad ID {ad.id}: No accepted rent request found for booked monthly advertisement."
                ))
                continue

            # Check if an invoice for the current month/year already exists for this ad and tenant
            # This prevents duplicate invoices if the command runs multiple times in a month
            existing_invoice = Invoice.objects.filter(
                advertisement=ad,
                payer=tenant,
                invoice_type=Invoice.MONTHLY,
                created_at__year=current_year,
                created_at__month=current_month
            ).first()

            if existing_invoice:
                self.stdout.write(self.style.NOTICE(
                    f"Skipping Ad ID {ad.id}: Monthly invoice for {current_month}/{current_year} already exists."
                ))
                continue

            # Generate a unique transaction ID
            tran_id = f"MON-{ad.owner.id}-{ad.id}-{current_year}{current_month}-{uuid.uuid4().hex[:6].upper()}"

            # Create the invoice
            Invoice.objects.create(
                advertisement=ad,
                payer=tenant,
                created_by=ad.owner,
                amount=ad.rent,
                invoice_type=Invoice.MONTHLY,
                transaction_id=tran_id,
                status=Invoice.PENDING,
                payment_method="sslcommerz" # Default payment method
            )
            self.stdout.write(self.style.SUCCESS(
                f"Generated monthly invoice for Ad ID {ad.id} (Tenant: {tenant.email}, Amount: {ad.rent})"
            ))

        self.stdout.write("Monthly invoice generation complete.")
