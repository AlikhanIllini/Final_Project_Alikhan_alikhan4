# Stock Cards

A web application for organizing and tracking U.S. stocks using a card-based interface. Each stock is represented as a card that stores core market data along with user-managed information such as notes, tags, and saved filters.

## Features

### 🎯 Core Features
- **Card-Based Stock Organization** - Each stock gets its own card with customizable notes and priority levels
- **Multi-User Authentication** - Secure user registration and login system
- **Real-Time Price Tracking** - Automatic price updates using Yahoo Finance API
- **Price History** - View historical price snapshots and percentage changes
- **Manual Price Fallback** - Enter prices manually when API is unavailable

### 🏷️ Organization
- **Custom Tags** - Create color-coded tags to categorize stocks
- **Saved Filters** - Save frequently-used filter combinations
- **Priority Levels** - High/Medium/Low priority for each card
- **Archive System** - Archive cards without deleting them

### 📊 Analytics
- **Price Change Tracking** - View 7-day and 30-day price change percentages
- **Weekly Email Digest** - Automated email summaries of notable movements
- **Price Caching** - 15-minute cache to reduce API calls

## Tech Stack

- **Backend**: Django 5.2.6 (Python 3.14)
- **Database**: SQLite
- **Stock Price API**: yfinance (Yahoo Finance)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Email**: Django console backend (development)

## Installation

### Prerequisites
- Python 3.14 (accessible via `python3` command)
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlikhanIllini/Final_Project_Alikhan_alikhan4.git
   cd Final_Project_Alikhan_alikhan4
   ```

2. **Install dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python3 manage.py migrate
   ```

4. **Create test data (optional)**
   ```bash
   python3 setup_test_data.py
   ```
   This creates:
   - Test user: `testuser` / `testpass123`
   - Admin user: `admin` / `admin123`
   - Sample stock cards with live prices

5. **Run the development server**
   ```bash
   python3 manage.py runserver
   ```

6. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Creating Your First Card

1. Register a new account or login
2. Click "Add Stock Card" from the dashboard
3. Enter a ticker symbol (e.g., `AAPL`, `GOOGL`)
4. Add notes, set priority, and assign tags
5. The system automatically fetches the current price

### Managing Tags

1. Navigate to the "Tags" page
2. Create custom tags with colors
3. Use tags to categorize your stocks
4. Filter dashboard by tags

### Weekly Digest

Run the management command to send weekly email summaries:

```bash
python3 manage.py send_weekly_digest
```

For testing:
```bash
python3 manage.py send_weekly_digest --test-email your@email.com
```

The digest includes:
- Stocks with ±5% or more movement
- Summary of active cards
- Notable price changes

### Manual Price Entry

If automatic price fetching fails:
1. Open the card detail page
2. Click "Add Price Manually"
3. Enter price and optional volume
4. Price will be marked as "Manual" source

## Project Structure

```
Final_Project_Alikhan_alikhan4/
├── appserver/                 # Django project settings
│   ├── settings.py           # Configuration
│   ├── urls.py               # Main URL routing
│   └── wsgi.py               # WSGI config
├── cards/                     # Main application
│   ├── models.py             # Data models
│   ├── views.py              # View logic
│   ├── forms.py              # Form definitions
│   ├── admin.py              # Admin customization
│   ├── price_adapter.py      # Stock price API integration
│   ├── templates/            # HTML templates
│   ├── static/               # CSS/JS files
│   ├── management/           # Custom commands
│   └── migrations/           # Database migrations
├── docs/                      # Project documentation
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── setup_test_data.py        # Test data generator
└── README.md                 # This file
```

## Data Models

### Stock
- Stores ticker symbols and company information
- Shared across all users

### StockCard
- User-specific stock tracking
- Contains notes, priority, target price
- Links to tags and price snapshots

### Tag
- User-defined categories
- Color-coded for visual organization

### PriceSnapshot
- Historical price data
- Tracks source (API or manual)
- Includes volume data

### SavedFilter
- Stores filter combinations
- Can be set as default

## Development

### Running Tests
```bash
python3 manage.py test
```

### Creating a Superuser
```bash
python3 manage.py createsuperuser
```

### Checking for Issues
```bash
python3 manage.py check
```

### Making Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## Author

Alikhan - [GitHub Repository](https://github.com/AlikhanIllini/Final_Project_Alikhan_alikhan4)

