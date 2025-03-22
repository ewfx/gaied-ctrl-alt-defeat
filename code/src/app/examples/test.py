"""
Example script to classify a sample email using the Email Classification API.
"""

import requests
import json
import base64
import os
from datetime import datetime
from pprint import pprint

# Sample email content
SAMPLE_EMAIL = """
From: client@acmecorp.com
To: loanservicing@commercialbank.com
Subject: Funding Request for Deal ABC123

Hello Loan Servicing Team,

We would like to request a funding transfer to our account for the Deal ABC123.

Details:
- Amount: $250,000.00
- Account Number: CLNT-123456-789
- Value Date: March 25, 2025
- Transaction Reference: FUND-25032025-001

Please let me know if you need any additional information.

Best regards,
John Smith
Financial Controller
ACME Corporation
"""

# Sample PDF attachment content (simulated)
SAMPLE_ATTACHMENT = """
FUNDING REQUEST FORM

Deal Name: ABC123
Client: ACME Corporation
Amount: $250,000.00
Currency: USD
Account Number: CLNT-123456-789
Value Date: 2025-03-25
Purpose: Working Capital

Authorized by:
John Smith
Financial Controller
ACME Corporation
"""

def main():
    # API endpoint
    api_url = "http://localhost:8000/classify-email-json"
    
    # Create temporary PDF file for attachment
    with open("temp_attachment.txt", "w") as f:
        f.write(SAMPLE_ATTACHMENT)
    
    # Read and encode attachment
    with open("temp_attachment.txt", "rb") as f:
        attachment_content = f.read()
        attachment_b64 = base64.b64encode(attachment_content).decode('utf-8')
    
    # Remove temporary file
    os.remove("temp_attachment.txt")
    
    # Prepare request payload
    payload = {
        "sender": "client@acmecorp.com",
        "subject": "Funding Request for Deal ABC123",
        "content": SAMPLE_EMAIL,
        "received_date": datetime.now().isoformat(),
        "attachments": [
            {
                "filename": "funding_request.txt",
                "content_type": "text/plain",
                "content_b64": attachment_b64
            }
        ],
        "thread_id": "sample-thread-123",
        "source": "api"
    }
    
    # Make API request
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        # Print results
        print("\n=== CLASSIFICATION RESULTS ===\n")
        result = response.json()
        
        print("Request Types:")
        for req_type in result["request_types"]:
            primary = "[PRIMARY]" if req_type["is_primary"] else ""
            print(f"  - {req_type['request_type']} / {req_type['sub_request_type']} (Confidence: {req_type['confidence']:.2f}) {primary}")
            print(f"    Reasoning: {req_type['reasoning']}")
        
        print("\nExtracted Fields:")
        for field in result["extracted_fields"]:
            print(f"  - {field['field_name']}: {field['value']} (Confidence: {field['confidence']:.2f}, Source: {field['source']})")
        
        print(f"\nProcessing Time: {result['processing_time_ms']:.2f}ms")
        print(f"Is Duplicate: {result['is_duplicate']}")
        if result["duplicate_reason"]:
            print(f"Duplicate Reason: {result['duplicate_reason']}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()