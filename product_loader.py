import pandas as pd
import json
import os
import re
from google import genai
from woocommerce import API
from dotenv import load_dotenv
import time
from typing import Dict, Any
import logging
from prompts import prompt

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MAX_RETRIES = 5


class WooCommerceProductLoader:
    def __init__(self):
        """Initialize the product loader with configuration"""
        self.woocommerce_url = os.getenv("WOOCOMMERCE_URL")
        self.consumer_key = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
        self.consumer_secret = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Validate required environment variables
        if not all(
            [
                self.woocommerce_url,
                self.consumer_key,
                self.consumer_secret,
                self.gemini_api_key,
            ]
        ):
            raise ValueError(
                "Missing required environment variables. Please check your .env file."
            )

        # Configure Gemini
        proxy_vars = ["all_proxy", "ALL_PROXY", "ftp_proxy", "FTP_PROXY"]
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
        self.client = genai.Client(api_key=self.gemini_api_key)

        # Configure WooCommerce API
        self.wcapi = API(
            url=self.woocommerce_url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version="wc/v3"
        )

        logger.info("WooCommerce Product Loader initialized successfully")

    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """Read product data from Excel file"""
        try:
            df = pd.read_excel(file_path, header=None, skiprows=1)

            expected_columns = [
                "product_name",
                "raw_features",
                "regular_price",
                "price",
            ]

            if len(df.columns) < len(expected_columns):
                raise ValueError(
                    f"Excel file has {len(df.columns)} columns, but {len(expected_columns)} are required"
                )

            df.columns = expected_columns + [
                f"extra_col_{i}" for i in range(len(df.columns) - len(expected_columns))
            ]

            df = df[expected_columns]

            logger.info(f"Successfully read {len(df)} products from {file_path}")
            logger.info(f"Columns assigned: {list(df.columns)}")

            return df
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            raise

    def process_with_gemini(
        self, product_name: str, raw_features: str
    ) -> Dict[str, Any]:
        """Process product through Gemini LLM to generate description and attributes"""
        for retry_count in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt.format(
                        product_name=product_name, raw_features=raw_features
                    ),
                )

                response_text = response.text.strip()

                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.rfind("```")
                    response_text = response_text[json_start:json_end].strip()

                parsed_response = json.loads(response_text)

                required_fields = ["slug", "description", "short_description", "attributes"]
                for field in required_fields:
                    if field not in parsed_response:
                        raise ValueError(f"Missing required field: {field}")

                logger.info(f"Successfully processed product: {product_name}")
                return parsed_response

            except Exception as e:
                error_message = str(e).lower()
                
                if "rate limit" in error_message or "quota" in error_message or "too many requests" in error_message:
                    retry_delay = None
                    
                    delay_patterns = [
                        r'retry after (\d+) seconds?',
                        r'wait (\d+) seconds?',
                        r'try again in (\d+) seconds?',
                        r'retry in (\d+) seconds?',
                        r'(\d+) seconds? before retrying'
                    ]
                    
                    for pattern in delay_patterns:
                        match = re.search(pattern, error_message)
                        if match:
                            retry_delay = int(match.group(1))
                            break
                    
                    if retry_delay is None:
                        retry_delay = 60
                    
                    if retry_count < MAX_RETRIES - 1:  # Don't sleep on last retry
                        logger.warning(f"Rate limit hit for {product_name}. Waiting {retry_delay} seconds before retry {retry_count + 2}/{MAX_RETRIES}")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded for {product_name} after {MAX_RETRIES} retries")
                        raise
                
                elif isinstance(e, json.JSONDecodeError):
                    logger.error(f"Failed to parse JSON response for {product_name}: {e}")
                    if retry_count < MAX_RETRIES - 1:
                        continue
                    else:
                        raise
                else:
                    # For other errors, log and retry or raise
                    logger.error(f"Error processing {product_name}: {e}")
                    if retry_count < MAX_RETRIES - 1:
                        continue
                    else:
                        raise

    def create_woocommerce_product(
        self, product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create product payload for WooCommerce API"""
        return {
            "name": product_data["product_name"],
            "slug": product_data["slug"],
            "type": "simple",
            "status": "draft",
            "regular_price": str(product_data["regular_price"]),
            "sale_price": str(product_data["price"]),
            "price": str(product_data["price"]),
            "description": product_data["description"],
            "short_description": product_data["short_description"],
            "attributes": product_data["attributes"],
        }

    def add_product_to_woocommerce(self, product_payload: Dict[str, Any]) -> bool:
        """Add product to WooCommerce via API"""
        try:
            response = self.wcapi.post("products", product_payload)
            
            if response.status_code in [200, 201]:
                logger.info(
                    f"Successfully added product {product_payload['name']} with id {response.json()['id']}"
                )
                return True
            else:
                logger.error(
                    f"Failed to add product {product_payload['name']}: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(
                f"Request error when adding product {product_payload['name']}: {e}"
            )
            return False

    def process_products(self, excel_file_path: str):
        """Main method to process all products from Excel file"""
        try:
            # Read Excel file
            df = self.read_excel_file(excel_file_path)

            successful_uploads = 0
            failed_uploads = 0

            for index, row in df.iterrows():
                try:
                    logger.info(
                        f"Processing product {index + 1}/{len(df)}: {row['product_name']}"
                    )

                    # Process with Gemini
                    gemini_response = self.process_with_gemini(
                        row["product_name"], str(row["raw_features"])
                    )

                    # Prepare product data
                    product_data = {
                        "product_name": row["product_name"],
                        "slug": gemini_response["slug"],
                        "price": row["price"],
                        "regular_price": row["regular_price"],
                        "description": gemini_response["description"],
                        "short_description": gemini_response["short_description"],
                        "attributes": gemini_response["attributes"],
                    }

                    # Create WooCommerce payload
                    woocommerce_payload = self.create_woocommerce_product(product_data)

                    # Add to WooCommerce
                    if self.add_product_to_woocommerce(woocommerce_payload):
                        successful_uploads += 1
                    else:
                        failed_uploads += 1

                    # Add delay to avoid rate limiting
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Error processing product {row['product_name']}: {e}")
                    failed_uploads += 1
                    continue

            logger.info(
                f"Processing complete. Successful: {successful_uploads}, Failed: {failed_uploads}"
            )

        except Exception as e:
            logger.error(f"Error in process_products: {e}")
            raise


def main():
    """Main function to run the product loader"""
    try:
        # Initialize the loader
        loader = WooCommerceProductLoader()

        # Process products from Excel file
        excel_file_path = "data/محصولات.xlsx"

        if not os.path.exists(excel_file_path):
            logger.error(f"Excel file not found: {excel_file_path}")
            return

        loader.process_products(excel_file_path)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
