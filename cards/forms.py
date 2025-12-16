"""
Forms for Stock Cards application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StockCard, Tag, SavedFilter, Stock, PriceSnapshot
from decimal import Decimal


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class StockCardForm(forms.ModelForm):
    """Form for creating/editing stock cards."""
    ticker = forms.CharField(
        max_length=10,
        help_text="Enter stock ticker symbol (e.g., AAPL, GOOGL)"
    )

    class Meta:
        model = StockCard
        fields = ['ticker', 'notes', 'priority', 'target_price', 'tags']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add notes about this stock...'}),
            'tags': forms.CheckboxSelectMultiple(),
            'priority': forms.RadioSelect(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filter tags to only show user's tags
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(user=user)

        # If editing existing card, populate ticker from stock
        if self.instance and self.instance.pk:
            self.fields['ticker'].initial = self.instance.stock.ticker
            self.fields['ticker'].widget.attrs['readonly'] = True

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker'].upper().strip()

        # If editing, ticker can't be changed
        if self.instance and self.instance.pk:
            return ticker

        # Check if user already has a card for this stock
        if self.user:
            stock = Stock.objects.filter(ticker=ticker).first()
            if stock and StockCard.objects.filter(user=self.user, stock=stock).exists():
                raise forms.ValidationError(f"You already have a card for {ticker}")

        return ticker

    def save(self, commit=True):
        card = super().save(commit=False)

        # Create or get stock
        ticker = self.cleaned_data['ticker']
        stock, created = Stock.objects.get_or_create(ticker=ticker)

        # If new stock, fetch company info
        if created:
            from .price_adapter import price_adapter
            info = price_adapter.get_stock_info(ticker)
            if info:
                stock.company_name = info.get('company_name', '')
                stock.exchange = info.get('exchange', '')
                stock.save()

        card.stock = stock
        card.user = self.user

        if commit:
            card.save()
            self.save_m2m()  # Save tags

        return card


class TagForm(forms.ModelForm):
    """Form for creating/editing tags."""

    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data['name']

        # Check for duplicate tag names for this user
        if self.user:
            existing = Tag.objects.filter(user=self.user, name=name)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(f"You already have a tag named '{name}'")

        return name

    def save(self, commit=True):
        tag = super().save(commit=False)
        tag.user = self.user

        if commit:
            tag.save()

        return tag


class SavedFilterForm(forms.ModelForm):
    """Form for creating/editing saved filters."""

    class Meta:
        model = SavedFilter
        fields = ['name', 'priority', 'tags', 'show_archived', 'sort_by', 'is_default']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filter tags to only show user's tags
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(user=user)

    def save(self, commit=True):
        filter_obj = super().save(commit=False)
        filter_obj.user = self.user

        if commit:
            filter_obj.save()
            self.save_m2m()  # Save tags

        return filter_obj


class ManualPriceForm(forms.ModelForm):
    """Form for manually entering stock prices (fallback when API fails)."""

    class Meta:
        model = PriceSnapshot
        fields = ['price', 'volume']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'volume': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, stock_card=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_card = stock_card

    def save(self, commit=True):
        snapshot = super().save(commit=False)
        snapshot.stock_card = self.stock_card
        snapshot.source = 'manual'

        if commit:
            snapshot.save()

        return snapshot

