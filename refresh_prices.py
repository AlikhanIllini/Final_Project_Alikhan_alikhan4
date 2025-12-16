#!/usr/bin/env python3
"""
Refresh stock prices for all existing cards.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appserver.settings')
django.setup()

from cards.models import StockCard, PriceSnapshot
from cards.price_adapter import price_adapter

def refresh_all_prices():
    print("Refreshing prices for all stock cards...")

    cards = StockCard.objects.all()
    success_count = 0
    fail_count = 0

    for card in cards:
        ticker = card.stock.ticker
        print(f"\nFetching price for {ticker}...", end=" ")

        price_data = price_adapter.get_stock_price(ticker)

        if price_data:
            # Create new price snapshot
            PriceSnapshot.objects.create(
                stock_card=card,
                price=price_data['price'],
                volume=price_data.get('volume', 0),
                source='api'
            )
            print(f"✓ ${price_data['price']}")
            success_count += 1
        else:
            print(f"✗ Failed")
            fail_count += 1

    print("\n" + "="*60)
    print(f"Refresh complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print("="*60)

if __name__ == "__main__":
    refresh_all_prices()

