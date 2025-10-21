# WooCommerce Product Loader

This Python script reads product data from an Excel file, processes it through Google's Gemini LLM to generate WooCommerce-compatible descriptions and attributes, and then adds the products to a WooCommerce store via API.

## Features

- Reads product data from Excel files with flexible column naming
- Uses Google Gemini AI to generate product descriptions and attributes
- Converts raw product features into structured WooCommerce attributes
- Adds products to WooCommerce via REST API
- Comprehensive error handling and logging
- Rate limiting to avoid API throttling

## Requirements

- Python 3.8+
- WooCommerce store with REST API enabled
- Google Gemini AI API key
- Excel file with product data

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Edit `.env` file with your actual credentials:
   ```
   WOOCOMMERCE_URL=https://yourstore.com
   WOOCOMMERCE_CONSUMER_KEY=ck_your_consumer_key
   WOOCOMMERCE_CONSUMER_SECRET=cs_your_consumer_secret
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Excel File Format

Your Excel file should have these columns (column names are flexible):
- **Product Name** (or "name", "product_name")
- **Raw Features** (or "features", "raw_features")
- **Price** (numeric)
- **Regular Price** (or "regular_price", numeric)

## Usage

1. Place your Excel file in the same directory as the script and name it `data/products.xlsx` (or modify the script to use a different filename)

2. Run the script:
   ```bash
   python product_loader.py
   ```

The script will:
1. Read products from the Excel file
2. Process each product through Gemini AI to generate:
   - Slug
   - Detailed description
   - Short description
   - Structured attributes
3. Add each product to your WooCommerce store

## WooCommerce API Setup

1. Go to your WordPress admin panel
2. Navigate to WooCommerce > Settings > Advanced > REST API
3. Click "Add Key"
4. Set permissions to "Read/Write"
5. Copy the Consumer Key and Consumer Secret to your `.env` file

## Gemini AI API Setup

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the API key to your `.env` file

Note: This script uses the new `google-genai` package with the Gemini 2.5 Flash model for improved performance.

## License

This project is open source and available under the MIT License.
