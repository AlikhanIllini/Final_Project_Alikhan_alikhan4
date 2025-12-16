#!/usr/bin/env python3
"""
Quick setup script for Stock Cards application.
Creates a test superuser and some sample data.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appserver.settings')
django.setup()

from django.contrib.auth.models import User
from cards.models import Stock, StockCard, Tag, PriceSnapshot
from cards.price_adapter import price_adapter
from decimal import Decimal

def setup_test_data():
    print("Setting up test data for Stock Cards...")

    # Create test user
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"

    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"✓ Created user: {username} / {password}")

    # Create superuser
    admin_username = "admin"
    admin_password = "admin123"

    if User.objects.filter(username=admin_username).exists():
        print(f"Admin user '{admin_username}' already exists.")
    else:
        User.objects.create_superuser(admin_username, "admin@example.com", admin_password)
        print(f"✓ Created admin: {admin_username} / {admin_password}")

    # Create sample tags
    tags_data = [
        {"name": "Tech", "color": "#3b82f6"},
        {"name": "Growth", "color": "#10b981"},
        {"name": "Watch", "color": "#f59e0b"},
    ]

    tags = []
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            user=user,
            name=tag_data["name"],
            defaults={"color": tag_data["color"]}
        )
        if created:
            print(f"✓ Created tag: {tag.name}")
        tags.append(tag)

    # Create sample stock cards
    sample_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    print("\nFetching stock data (this may take a moment)...")

    for ticker in sample_tickers:
        # Check if card already exists
        stock, _ = Stock.objects.get_or_create(ticker=ticker)

        if StockCard.objects.filter(user=user, stock=stock).exists():
            print(f"  Card for {ticker} already exists, skipping.")
            continue

        # Fetch stock info
        price_data = price_adapter.get_stock_price(ticker)

        if price_data:
            # Update stock info
            if not stock.company_name:
                stock.company_name = price_data.get('company_name', '')
                stock.exchange = price_data.get('exchange', '')
                stock.save()

            # Create card
            card = StockCard.objects.create(
                user=user,
                stock=stock,
                priority=2,
                notes=f"Sample card for {ticker}"
            )

            # Add tags
            card.tags.add(tags[0])  # Add Tech tag

            # Create price snapshot
            PriceSnapshot.objects.create(
                stock_card=card,
                price=price_data['price'],
                volume=price_data.get('volume', 0),
                source='api'
            )

            print(f"✓ Created card for {ticker} - ${price_data['price']}")
        else:
            print(f"  Failed to fetch price for {ticker}, creating card without price")
            card = StockCard.objects.create(
                user=user,
                stock=stock,
                priority=2,
                notes=f"Sample card for {ticker} (price fetch failed)"
            )

    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print(f"\nTest User:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"\nAdmin User:")
    print(f"  Username: {admin_username}")
    print(f"  Password: {admin_password}")
    print(f"\nRun the server with:")
    print(f"  python3 manage.py runserver")
    print(f"\nThen visit:")
    print(f"  http://127.0.0.1:8000/")
    print()

if __name__ == "__main__":
    setup_test_data()

