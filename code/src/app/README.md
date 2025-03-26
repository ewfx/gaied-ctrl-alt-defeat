# Email Classification System

A powerful API for automatically classifying commercial bank lending service emails and extracting relevant information for service requests.

## Core Features

### Intelligent Email Processing
- **Multi-format Support**: Process emails in various formats including EML files, PDF email chains, and raw email content
- **Attachment Processing**: Extract and analyze content from PDF, Word, HTML, text files, and images using OCR
- **HTML Content Extraction**: Clean and extract text from HTML email bodies
- **Metadata Extraction**: Parse email headers for sender, recipient, dates, IDs, and references

### Advanced Classification
- **Request Type Identification**: Classify emails into primary and secondary request types with confidence scores
- **Sub-request Classification**: Identify specific sub-categories within each request type
- **Priority Detection**: Determine the primary intent when emails contain multiple requests
- **Reasoning Transparency**: Provide detailed explanations for classification decisions

### Intelligent Duplicate Detection
- **Semantic Similarity**: Compare email content using embeddings to detect duplicates even with wording variations
- **Metadata Comparison**: Use sender, recipient, thread ID, IP address, and other metadata for detection
- **Confidence Scoring**: Provide granular confidence levels for duplicate detection
- **Time Window Analysis**: Consider time proximity in duplicate detection with configurable windows
- **Caching System**: Efficient LRU caching of processed emails for performance

### Data Extraction
- **Field Extraction**: Extract structured data like amounts, account numbers, transaction IDs
- **Source Prioritization**: Prioritize data sources (email body vs. attachments) based on field type
- **Confidence Scoring**: Assign confidence levels to extracted values
- **Format Normalization**: Standardize dates, currency values, and other fields

### Robust Architecture
- **API Key Management**: Rate-limited API keys with automatic rotation capability
- **Multi-LLM Support**: Flexible integration with various LLM providers (Anthropic, OpenAI, OpenRouter)
- **Task-specific LLM Routing**: Use different models for classification vs. data extraction
- **Error Handling**: Comprehensive error handling and fallback mechanisms
- **Analytics Collection**: Record classification results and duplicate detection metrics

## Project Structure

```
app/
├── api
│   ├── analytics.py
│   ├── __init__.py
│   ├── request_types.py
│   └── routes.py
├── config.py
├── core
│   ├── api_manager.py
│   ├── config.py
│   ├── __init__.py
│   └── llm_handler.py
├── db
│   ├── __init__.py
│   └── session.py
├── __init__.py
├── main.py
├── models
│   ├── __init__.py
│   ├── request_models.py
│   ├── request_types.py
│   └── response_models.py
├── README.md
├── schemas
│   ├── analytics.py
│   ├── __init__.py
│   └── request_types.py
└── services
    ├── classification_service.py
    ├── data_extractor.py
    ├── duplicate_detector.py
    ├── email_processor.py
    ├── __init__.py
    └── IntelligentDuplicateDetector.py
```

## API Endpoints

### Classification Endpoints

#### `POST /classify-email-chain`
Process an email chain from a PDF file with optional attachments.

**Parameters**:
- `email_chain_file`: PDF file containing the email chain (File upload)
- `attachments`: Optional list of attachment files (Multiple file uploads)
- `thread_id`: Optional thread ID for duplicate detection (Form field)

**Response**: `ClassificationResponse` object

#### `POST /classify-eml`
Process an email from an EML file.

**Parameters**:
- `eml_file`: EML file containing the email with attachments (File upload)
- `thread_id`: Optional thread ID for duplicate detection (Form field)

**Response**: `ClassificationResponse` object

### Request Type Management Endpoints

#### `GET /request-types`
Retrieve all request types and their sub-types.

#### `POST /request-types`
Create a new request type.

#### `GET /request-types/{request_type_id}`
Get details for a specific request type.

#### `PUT /request-types/{request_type_id}`
Update an existing request type.

#### `DELETE /request-types/{request_type_id}`
Delete a request type.

#### Sub-request Type Management
- `GET /request-types/{request_type_id}/sub-request-types`: Get all sub-request types
- `POST /request-types/{request_type_id}/sub-request-types`: Add a new sub-request type
- `PUT /request-types/{request_type_id}/sub-request-types/{subrequest_type_id}`: Update a sub-request type
- `DELETE /request-types/{request_type_id}/sub-request-types/{subrequest_type_id}`: Remove a sub-request type

## Data Models

### Classification Response

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
  "support_group": "Commercial Lending Team",
  "is_duplicate": false,
  "duplicate_reason": null,
  "duplicate_confidence": 0.0,
  "duplicate_id": null,
  "processing_time_ms": 1250.5,
  "error": null
}
```

### Request Type Definition

```json
{
  "name": "Money Movement-Inbound",
  "definition": "Requests related to incoming funds transactions",
  "support_group": "Commercial Lending Team",
  "sub_request_types": [
    {
      "_id": "60f1a2b3c4d5e6f7a8b9c0d1",
      "name": "Principal",
      "definition": "Inbound transfer of loan principal amounts",
      "required_attributes": ["amount", "account_number", "value_date", "transaction_id"]
    }
  ]
}
```

## Configuration Options

The system provides numerous configuration options for fine-tuning:

### Duplicate Detection
- `duplicate_cache_days`: Number of days to keep emails in cache (default: 14)
- `duplicate_cache_size`: Maximum number of emails in cache (default: 10000)
- `semantic_threshold`: Threshold for considering content semantically similar (default: 0.8)
- `metadata_weight`: Weight to give metadata vs content in duplicate detection (default: 0.25)
- `subject_weight`: Weight for subject vs body in content similarity (default: 0.45)
- `content_weight`: Weight for content in overall similarity (default: 0.9)
- `time_window_hours`: Time window to consider for duplicates in hours (default: 72)

### Content Processing
- `max_attachment_size_mb`: Maximum attachment size in MB (default: 10)
- `embedding_model`: Model to use for text embeddings (default: "all-MiniLM-L6-v2")

## Key Components

### EmailProcessor
Handles extraction of text and metadata from email content and attachments. Provides methods for processing different file types including PDFs, Word documents, HTML, and images.

### IntelligentDuplicateDetector
Identifies duplicate emails using semantic content similarity and metadata comparison. Uses embedding-based similarity detection with configurable thresholds and weights.

### ClassificationService
Orchestrates the email classification workflow, managing the processing of emails, duplicate detection, request type identification, and field extraction.

### DataExtractor
Extracts structured field data from emails based on identified request types, with source prioritization and confidence scoring.

### LLMHandler
Manages interactions with language model providers, handling API key rotation and model selection based on the task type.

## Advanced Features

### Intelligent Embedding-based Similarity
The system uses text embeddings to detect semantic similarity between emails, allowing it to identify duplicates even when the wording varies. For environments without access to external embedding services, it includes a fallback MockEmbeddingProvider.

### Time-aware Duplicate Detection
The duplicate detection system considers time proximity between emails, recognizing that emails closer in time are more likely to be duplicates.

### Thread-based Correlation
Uses email thread IDs, message IDs, references, and in-reply-to headers to correlate related emails and improve duplicate detection.

### API Key Rotation & Rate Limiting
Supports multiple API keys per service with automatic rotation based on usage limits, ensuring uninterrupted service even when rate limits are approached.

### Fallback Mechanisms
Multiple fallback systems ensure the service continues functioning even when components fail:
- Mock embedding provider when advanced embedding services aren't available
- Default metadata when extraction fails
- JSON fixing for malformed LLM responses