#!/usr/bin/env python3
"""
Test script for Google Genai integration
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def test_genai():
    """Test the new Google Genai client"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return
    
    try:
        proxy_vars = ['all_proxy', 'ALL_PROXY', 'ftp_proxy', 'FTP_PROXY']
        for var in proxy_vars:
                del os.environ[var]

        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents='Hello, please respond with "Google Genai is working correctly!"'
        )
        
        print("✅ Google Genai test successful!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Google Genai test failed: {e}")

if __name__ == "__main__":
    test_genai()
