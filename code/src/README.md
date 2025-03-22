# Email Classification System

This project provides an API for automatically classifying commercial bank lending service emails and extracting relevant information for service requests.

## Features

- **Email Classification**: Identifies request types and sub-request types from email content and attachments
- **Data Extraction**: Extracts relevant fields based on the identified request type
- **Duplicate Detection**: Identifies duplicate emails to prevent redundant service requests
- **Multi-Request Handling**: Supports emails containing multiple request types with primary intent detection
- **Priority-based Extraction**: Customizable extraction rules with source prioritization
- **Document Processing**: Handles various attachment types (PDF, Word, text, etc.)
- **API Key Management**: Robust API key rotation with rate limiting

## Project Structure

```
email-classification-system/
│
├── app/                           # Main application code
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration settings
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py              # API routes
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── api_manager.py         # API key management
│   │   └── llm_handler.py         # LLM integration
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── request_models.py      # Request data models
│   │   └── response_models.py     # Response data models
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── email_processor.py     # Email and attachment processing
│   │   ├── classification_service.py # Classification orchestration
│   │   ├── duplicate_detector.py  # Duplicate email detection
│   │   └── data_extractor.py      # Field extraction from emails
│   └── data/                      # Configuration data
│       ├── request_types.json     # Request type definitions
│       └── extraction_rules.json  # Field extraction rules
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- API keys for LLM services (Anthropic, OpenAI, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-classification-system.git
   cd email-classification-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys and configuration.

### Running the Application

Start the FastAPI server:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000` and the Swagger documentation at `http://localhost:8000/docs`.

## API Usage

### Classify Email

```
POST /classify-email
```

Form data:
- `email_content`: The body content of the email
- `sender`: Email address of the sender
- `subject`: Email subject line
- `received_date`: Date when the email was received (ISO format)
- `thread_id` (optional): Thread ID for duplicate detection
- `source` (optional): Source of the email (outlook, gmail, api, other)
- `attachments` (optional): File attachments

### Classify Email (JSON)

```
POST /classify-email-json
```

JSON body:
```json
{
  "sender": "client@example.com",
  "subject": "Request for funds transfer",
  "content": "Hello, We need to transfer $50,000 to account XYZ. Best regards, Client",
  "received_date": "2023-11-15T10:30:00Z",
  "attachments": [
    {
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "content_b64": "JVBERi0xLjMKJcTl8uXrp/Ln..."
    }
  ],
  "thread_id": "thread-12345",
  "source": "outlook"
}
```

### Get Request Types

```
GET /request-types
```

Returns all supported request types and sub-request types.

### Health Check

```
GET /health
```

Returns the current health status of the system, including API key usage information.

### Reset API Keys

```
POST /reset-api-keys
```

Resets all API key usage counters.

## Response Format

```json
{
  "request_types": [
    {
      "request_type": "Money Movement-Inbound",
      "sub_request_type": "Principal",
      "confidence": 0.95,
      "reasoning": "Email explicitly mentions transferring funds to an account",
      "is_primary": true
    }
  ],
  "extracted_fields": [
    {
      "field_name": "amount",
      "value": 50000,
      "confidence": 0.98,
      "source": "email_body"
    },
    {
      "field_name": "account_number",
      "value": "XYZ",
      "confidence": 0.85,
      "source": "email_body"
    }
  ],
  "is_duplicate": false,
  "duplicate_reason": null,
  "processing_time_ms": 1250.5,
  "error": null
}
```

## Configuration

### Request Types

Request types are defined in `app/data/request_types.json`. You can modify this file to add or change request types and sub-request types.

### Extraction Rules

Extraction rules are defined in `app/data/extraction_rules.json`. These rules specify which fields to extract for each request type and the priority of sources.

### Environment Variables

- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DUPLICATE_CACHE_DAYS`: Number of days to keep emails in cache for duplicate detection (default: 7)
- `MAX_ATTACHMENT_SIZE_MB`: Maximum attachment size in MB (default: 10)

API keys should be added in the format `SERVICE_API_KEY_LIMIT_PERIOD_INDEX`, for example:
- `ANTHROPIC_API_KEY_50_60_1`: Anthropic API key with 50 calls per 60 minutes

## Testing

Run tests with pytest:

```bash
pytest
```

## Deployment

### Docker

Build the Docker image:

```bash
docker build -t email-classification-system .
```

Run the container:

```bash
docker run -d -p 8000:8000 --env-file .env email-classification-system
```

### Cloud Deployment

The application can be deployed to any cloud platform that supports containerized applications, such as:
- AWS Elastic Container Service (ECS)
- Google Cloud Run
- Azure Container Instances

## License

This project is licensed under the MIT License - see the LICENSE file for details.