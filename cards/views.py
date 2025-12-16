from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import StockCard, Tag, SavedFilter, Stock, PriceSnapshot
from .forms import (
    UserRegistrationForm, StockCardForm, TagForm,
    SavedFilterForm, ManualPriceForm
)
from .price_adapter import price_adapter


def home(request):
    """Landing page - redirects to dashboard if authenticated."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'cards/home.html')


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Stock Cards.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    """Main dashboard showing user's stock cards."""
    # Get filter parameters
    priority_filter = request.GET.get('priority')
    tag_filter = request.GET.get('tag')
    show_archived = request.GET.get('archived') == 'true'
    sort_by = request.GET.get('sort', 'priority')
    search = request.GET.get('search', '').strip()

    # Base queryset
    cards = StockCard.objects.filter(user=request.user)

    # Apply filters
    if not show_archived:
        cards = cards.filter(is_archived=False)

    if priority_filter:
        cards = cards.filter(priority=priority_filter)

    if tag_filter:
        cards = cards.filter(tags__id=tag_filter)

    if search:
        cards = cards.filter(
            Q(stock__ticker__icontains=search) |
            Q(stock__company_name__icontains=search) |
            Q(notes__icontains=search)
        )

    # Apply sorting
    sort_options = {
        'priority': ['priority', '-updated_at'],
        'updated_at': ['-updated_at'],
        'created_at': ['-created_at'],
        'ticker': ['stock__ticker'],
    }
    cards = cards.order_by(*sort_options.get(sort_by, ['priority', '-updated_at']))

    # Get distinct cards (in case tag filter created duplicates)
    cards = cards.distinct()

    # Get user's tags for filter dropdown
    user_tags = Tag.objects.filter(user=request.user)

    # Get saved filters
    saved_filters = SavedFilter.objects.filter(user=request.user)

    context = {
        'cards': cards,
        'user_tags': user_tags,
        'saved_filters': saved_filters,
        'current_priority': priority_filter,
        'current_tag': tag_filter,
        'show_archived': show_archived,
        'current_sort': sort_by,
        'search_query': search,
    }

    return render(request, 'cards/dashboard.html', context)


@login_required
def card_create(request):
    """Create a new stock card."""
    if request.method == 'POST':
        form = StockCardForm(request.POST, user=request.user)
        if form.is_valid():
            card = form.save()

            # Fetch and save initial price
            ticker = card.stock.ticker
            price_data = price_adapter.get_stock_price(ticker)

            if price_data:
                PriceSnapshot.objects.create(
                    stock_card=card,
                    price=price_data['price'],
                    volume=price_data.get('volume', 0),
                    source='api'
                )
                messages.success(
                    request,
                    f'Stock card for {ticker} created successfully! Current price: ${price_data["price"]}'
                )
            else:
                messages.warning(
                    request,
                    f'Stock card for {ticker} created, but price fetch failed. You can add price manually.'
                )

            return redirect('dashboard')
    else:
        form = StockCardForm(user=request.user)

    return render(request, 'cards/card_form.html', {
        'form': form,
        'title': 'Create Stock Card',
        'button_text': 'Create Card'
    })


@login_required
def card_edit(request, card_id):
    """Edit an existing stock card."""
    card = get_object_or_404(StockCard, id=card_id, user=request.user)

    if request.method == 'POST':
        form = StockCardForm(request.POST, instance=card, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Card for {card.stock.ticker} updated successfully!')
            return redirect('dashboard')
    else:
        form = StockCardForm(instance=card, user=request.user)

    return render(request, 'cards/card_form.html', {
        'form': form,
        'card': card,
        'title': f'Edit {card.stock.ticker}',
        'button_text': 'Save Changes'
    })


@login_required
def card_detail(request, card_id):
    """View detailed information about a stock card."""
    card = get_object_or_404(StockCard, id=card_id, user=request.user)

    # Get price history (last 30 snapshots)
    price_history = card.price_snapshots.all()[:30]

    # Get latest price
    latest_price = card.get_latest_price()

    # Calculate price changes
    price_change_7d = card.get_price_change_percentage(days=7)
    price_change_30d = card.get_price_change_percentage(days=30)

    context = {
        'card': card,
        'latest_price': latest_price,
        'price_history': price_history,
        'price_change_7d': price_change_7d,
        'price_change_30d': price_change_30d,
    }

    return render(request, 'cards/card_detail.html', context)


@login_required
def card_delete(request, card_id):
    """Delete a stock card."""
    card = get_object_or_404(StockCard, id=card_id, user=request.user)

    if request.method == 'POST':
        ticker = card.stock.ticker
        card.delete()
        messages.success(request, f'Card for {ticker} deleted successfully!')
        return redirect('dashboard')

    return render(request, 'cards/card_confirm_delete.html', {'card': card})


@login_required
def card_archive(request, card_id):
    """Archive/unarchive a stock card."""
    card = get_object_or_404(StockCard, id=card_id, user=request.user)
    card.is_archived = not card.is_archived
    card.save()

    status = 'archived' if card.is_archived else 'unarchived'
    messages.success(request, f'Card for {card.stock.ticker} {status} successfully!')

    return redirect('dashboard')


@login_required
def refresh_price(request, card_id):
    """Refresh stock price for a card."""
    card = get_object_or_404(StockCard, id=card_id, user=request.user)

    price_data = price_adapter.get_stock_price(card.stock.ticker)

    if price_data:
        PriceSnapshot.objects.create(
            stock_card=card,
            price=price_data['price'],
            volume=price_data.get('volume', 0),
            source='api'
        )
        messages.success(request, f'Price updated: ${price_data["price"]}')
    else:
        messages.error(request, 'Failed to fetch price. Try manual entry.')
        return redirect('manual_price', card_id=card.id)

    return redirect('card_detail', card_id=card.id)


@login_required
def manual_price(request, card_id):
    """Manually enter stock price when API fails."""
    card = get_object_or_404(StockCard, id=card_id, user=request.user)

    if request.method == 'POST':
        form = ManualPriceForm(request.POST, stock_card=card)
        if form.is_valid():
            snapshot = form.save()
            messages.success(request, f'Price manually added: ${snapshot.price}')
            return redirect('card_detail', card_id=card.id)
    else:
        form = ManualPriceForm(stock_card=card)

    return render(request, 'cards/manual_price_form.html', {
        'form': form,
        'card': card
    })


@login_required
def tag_list(request):
    """List all user's tags."""
    tags = Tag.objects.filter(user=request.user)
    return render(request, 'cards/tag_list.html', {'tags': tags})


@login_required
def tag_create(request):
    """Create a new tag."""
    if request.method == 'POST':
        form = TagForm(request.POST, user=request.user)
        if form.is_valid():
            tag = form.save()
            messages.success(request, f'Tag "{tag.name}" created successfully!')
            return redirect('tag_list')
    else:
        form = TagForm(user=request.user)

    return render(request, 'cards/tag_form.html', {
        'form': form,
        'title': 'Create Tag',
        'button_text': 'Create Tag'
    })


@login_required
def tag_edit(request, tag_id):
    """Edit a tag."""
    tag = get_object_or_404(Tag, id=tag_id, user=request.user)

    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tag "{tag.name}" updated successfully!')
            return redirect('tag_list')
    else:
        form = TagForm(instance=tag, user=request.user)

    return render(request, 'cards/tag_form.html', {
        'form': form,
        'tag': tag,
        'title': f'Edit Tag: {tag.name}',
        'button_text': 'Save Changes'
    })


@login_required
def tag_delete(request, tag_id):
    """Delete a tag."""
    tag = get_object_or_404(Tag, id=tag_id, user=request.user)

    if request.method == 'POST':
        name = tag.name
        tag.delete()
        messages.success(request, f'Tag "{name}" deleted successfully!')
        return redirect('tag_list')

    return render(request, 'cards/tag_confirm_delete.html', {'tag': tag})

