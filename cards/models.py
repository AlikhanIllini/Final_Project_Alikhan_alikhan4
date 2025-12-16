from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class Stock(models.Model):
    """
    Represents a stock ticker symbol with basic information.
    This is shared across all users to avoid duplicate stock data.
    """
    ticker = models.CharField(max_length=10, unique=True, db_index=True)
    company_name = models.CharField(max_length=255, blank=True)
    exchange = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ticker']

    def __str__(self):
        return f"{self.ticker} - {self.company_name}" if self.company_name else self.ticker


class Tag(models.Model):
    """
    User-defined tags for categorizing stock cards.
    Each tag belongs to a specific user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6B7280')  # Hex color code
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class StockCard(models.Model):
    """
    A user's tracked stock card with notes, priority, and tags.
    This is the core model for organizing stocks.
    """
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_cards')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='cards')
    tags = models.ManyToManyField(Tag, blank=True, related_name='stock_cards')

    # User-managed fields
    notes = models.TextField(blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)]
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Card state
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['priority', '-updated_at']
        unique_together = ['user', 'stock']
        indexes = [
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['user', 'is_archived']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.stock.ticker}"

    def get_latest_price(self):
        """Get the most recent price snapshot for this card."""
        return self.price_snapshots.order_by('-timestamp').first()

    def get_price_change_percentage(self, days=7):
        """Calculate price change percentage over the specified days."""
        latest = self.price_snapshots.order_by('-timestamp').first()
        if not latest:
            return None

        past_date = timezone.now() - timezone.timedelta(days=days)
        past_price = self.price_snapshots.filter(
            timestamp__lte=past_date
        ).order_by('-timestamp').first()

        if not past_price or past_price.price == 0:
            return None

        change = ((latest.price - past_price.price) / past_price.price) * 100
        return round(change, 2)


class PriceSnapshot(models.Model):
    """
    Stores historical price data for stock cards.
    This allows users to track price changes over time.
    """
    stock_card = models.ForeignKey(
        StockCard,
        on_delete=models.CASCADE,
        related_name='price_snapshots'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Additional price data
    volume = models.BigIntegerField(null=True, blank=True)
    source = models.CharField(
        max_length=20,
        choices=[('api', 'API'), ('manual', 'Manual')],
        default='api'
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['stock_card', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.stock_card.stock.ticker} - ${self.price} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SavedFilter(models.Model):
    """
    Stores user's saved filter combinations for the dashboard.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_filters')
    name = models.CharField(max_length=100)

    # Filter criteria (stored as JSON-like fields)
    priority = models.IntegerField(
        null=True,
        blank=True,
        choices=StockCard.PRIORITY_CHOICES
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='saved_filters')
    show_archived = models.BooleanField(default=False)

    # Sorting
    sort_by = models.CharField(
        max_length=20,
        choices=[
            ('priority', 'Priority'),
            ('updated_at', 'Recently Updated'),
            ('created_at', 'Recently Created'),
            ('ticker', 'Ticker Symbol'),
        ],
        default='priority'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def save(self, *args, **kwargs):
        """Ensure only one default filter per user."""
        if self.is_default:
            SavedFilter.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
