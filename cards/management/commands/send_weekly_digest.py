"""
Django management command for sending weekly stock digest emails.
Run with: python3 manage.py send_weekly_digest
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from cards.models import StockCard, PriceSnapshot


class Command(BaseCommand):
    help = 'Send weekly digest emails to all users with notable stock movements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-email',
            type=str,
            help='Send test digest to specific email address',
        )

    def handle(self, *args, **options):
        test_email = options.get('test_email')

        if test_email:
            self.stdout.write(f'Sending test digest to {test_email}...')
            self.send_digest_to_email(test_email, test_mode=True)
            self.stdout.write(self.style.SUCCESS(f'Test digest sent to {test_email}'))
            return

        users = User.objects.filter(is_active=True)
        sent_count = 0

        for user in users:
            if user.email:
                self.send_digest_to_user(user)
                sent_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {sent_count} weekly digest emails')
        )

    def send_digest_to_user(self, user):
        """Send weekly digest to a specific user."""
        cards = StockCard.objects.filter(user=user, is_archived=False)

        if not cards.exists():
            return

        # Collect notable movements (>5% change in last 7 days)
        notable_cards = []
        for card in cards:
            change = card.get_price_change_percentage(days=7)
            if change is not None and abs(change) >= 5:
                latest_price = card.get_latest_price()
                notable_cards.append({
                    'ticker': card.stock.ticker,
                    'company': card.stock.company_name,
                    'change': change,
                    'price': latest_price.price if latest_price else None,
                })

        # Build email
        subject = f'📈 Stock Cards Weekly Digest - {timezone.now().strftime("%B %d, %Y")}'
        message = self.build_email_message(user, cards, notable_cards)

        send_mail(
            subject,
            message,
            None,  # Use DEFAULT_FROM_EMAIL
            [user.email],
            fail_silently=False,
        )

    def send_digest_to_email(self, email, test_mode=False):
        """Send test digest to specific email."""
        from django.contrib.auth.models import User

        # Use first user's data for test, or create sample data
        user = User.objects.first()
        if not user:
            message = "No users in database. Create a user first."
            subject = "Stock Cards Test Digest"
        else:
            cards = StockCard.objects.filter(user=user, is_archived=False)
            notable_cards = []

            for card in cards[:5]:  # Limit to 5 for test
                change = card.get_price_change_percentage(days=7)
                latest_price = card.get_latest_price()
                if change is not None:
                    notable_cards.append({
                        'ticker': card.stock.ticker,
                        'company': card.stock.company_name,
                        'change': change,
                        'price': latest_price.price if latest_price else None,
                    })

            subject = f'📈 Stock Cards Weekly Digest (TEST) - {timezone.now().strftime("%B %d, %Y")}'
            message = self.build_email_message(user, cards, notable_cards)

        send_mail(
            subject,
            message,
            None,
            [email],
            fail_silently=False,
        )

    def build_email_message(self, user, cards, notable_cards):
        """Build the email message content."""
        message_parts = [
            f'Hello {user.username},\n',
            f'Here is your weekly Stock Cards digest for {timezone.now().strftime("%B %d, %Y")}.\n',
            '\n' + '='*60 + '\n',
        ]

        # Notable movements section
        if notable_cards:
            message_parts.append('\n📊 NOTABLE MOVEMENTS (±5% or more):\n')
            message_parts.append('-'*60 + '\n')

            for card_data in notable_cards:
                arrow = '📈' if card_data['change'] > 0 else '📉'
                sign = '+' if card_data['change'] > 0 else ''

                message_parts.append(
                    f"\n{arrow} {card_data['ticker']} - {card_data['company']}\n"
                    f"   Current Price: ${card_data['price']}\n"
                    f"   7-Day Change: {sign}{card_data['change']:.2f}%\n"
                )
        else:
            message_parts.append('\n📊 No significant movements this week (±5% threshold).\n')

        # Summary section
        message_parts.append('\n' + '='*60 + '\n')
        message_parts.append(f'\n📋 SUMMARY:\n')
        message_parts.append(f'   Total Active Cards: {cards.count()}\n')
        message_parts.append(f'   Notable Movements: {len(notable_cards)}\n')

        # Footer
        message_parts.append('\n' + '='*60 + '\n')
        message_parts.append('\nVisit your dashboard to see more details.\n')
        message_parts.append('\nHappy investing!\n')
        message_parts.append('- Stock Cards Team\n')

        return ''.join(message_parts)

