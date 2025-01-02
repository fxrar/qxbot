# QuoteX Trading Bot

An automated trading bot built with Python and Selenium for QuoteX platform.

## Overview

This bot automates trading operations on the QuoteX platform using Python and Selenium for web automation. It handles account login and trading operations automatically.

## Prerequisites

- Python 3.x
- Selenium WebDriver
- Chrome Browser

## Project Files

**Main Components:**
- `qx.py` - Main bot script that handles trading operations
- `config.yml` - Configuration settings for the bot
- `killer.js` - JavaScript helper functions
- `killer.bat` - Batch script for Windows execution

## Setup Instructions

1. Install Python dependencies:
```bash
pip install selenium
```

2. Configure Login Credentials:
   - Open `qx.py`
   - Navigate to line 650
   - Update email and password details

## File Structure

| File | Description |
|------|-------------|
| qx.py | Core bot implementation with trading logic |
| config.yml | Bot configuration and settings |
| killer.js | JavaScript utilities for enhanced functionality |
| killer.bat | Windows execution script |

## Configuration

To modify login credentials:
```python
# Located at line 650 in qx.py
EMAIL = "your_email@example.com"
PASSWORD = "your_password"
```

## Usage

1. Ensure all prerequisites are installed
2. Configure your credentials in `qx.py`
3. Run the bot:
```bash
python qx.py
```



# ❤️ Support
Want to support me? Oh I don't need any help right now but nature does! Support nature by donating to The Nature Conservancy or spread the word if you can't donate.

**Donate Here** : https://www.nature.org/en-us/membership-and-giving/donate-to-our-mission/

Made with ❤️ by h1ac & fxrar

The bot utilizes Selenium WebDriver to interact with the QuoteX platform, automating trading operations through Python scripts. It maintains session persistence and handles automated login processes.

