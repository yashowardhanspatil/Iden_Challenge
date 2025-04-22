# Iden_Challenge

A Python web scraper that automates the extraction of product data from the IDEN hiring challenge website.

## Overview

This script automates the following workflow:
1. Login to the IDEN hiring challenge website
2. Navigate to the products page via the menu system
3. Click the "Load Table" button to load product data
4. Extract product information from the page
5. Save the extracted data as a JSON file

## Requirements

- Python 3.7+
- Async Playwright for Python
- python-dotenv

## Installation

1. Clone this repository or download the script

2. Install dependencies:
   ```bash
   pip install playwright python-dotenv
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

4. Create a `.env` file in the same directory as the script with your credentials:
   ```
   IDEN_USERNAME=your_email@example.com
   IDEN_PASSWORD=your_password
   ```

## Usage

Run the script with:

```bash
python scraper.py
```

The script will:
- Open a browser window (visible by default)
- Log in to the IDEN hiring challenge website
- Navigate to the products page
- Click "Load Table" to load the product data
- Extract product information
- Save the data to `products.json` in the current directory

## Output

The script generates a JSON file (`products.json`) containing the extracted product data with the following structure:

```json
[
    {
        "ID": "product-id-1",
        "Dimensions": "dimensions-value",
        "Details": "details-value",
        "Type": "type-value"
    },
    ...
]
```

## Customization

- To run the browser in headless mode (invisible), change `headless=False` to `headless=True` in the `load_or_login` function
- To change the output file name, modify the `OUTPUT_JSON` variable at the top of the script

## Troubleshooting

If you encounter issues:

1. **Login Problems**: Verify your credentials in the `.env` file
2. **Navigation Failures**: The script includes fallback direct URL navigation if menu navigation fails
3. **Extraction Issues**: Check the product container selectors in the `extract_products` function and adjust them based on the actual HTML structure
4. **Load Table Button Not Found**: Inspect the button in your browser and update the selectors in the `navigate_to_products` function

## Session Management

The script saves the session state to `session.json` after a successful login. This file can potentially be used for future development to restore sessions.
