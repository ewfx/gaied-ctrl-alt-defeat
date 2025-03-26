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
gaied-ctrl-alt-defeat/
├── artifacts
│   ├── arch         # Architecture documentation
│   └── demo         # Demo materials
├── code
│   ├── src
│   │   ├── app      # Python backend
│   │   ├── client   # Next.js frontend
│   │   ├── Dockerfile
│   │   ├── llm-config.json
│   │   └── requirements.txt
│   └── test         # Test files
├── LICENSE
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 18.0 or higher
- API keys for LLM services (if applicable)

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv hackathon
   source hackathon/bin/activate  # On Windows: hackathon\Scripts\activate
   # For fish shell:
   source hackathon/bin/activate.fish
   ```

2. Navigate to the source directory:
   ```bash
   cd gaied-ctrl-alt-defeat/code/src/
   ```

3. Create a `.env` file in the app directory:
   ```bash
   cd app
   touch .env
   ```

4. Add the following environment variables to the `.env` file:
   ```
   # Anthropic API keys
   OPENROUTER_API_KEY_10_1_1=your_open_router_key_1
   OPENROUTER_API_KEY_10_1_2=your_open_router_key_2

   # Application settings
   PORT=8000
   LOG_LEVEL=INFO
   DUPLICATE_CACHE_DAYS=7
   MONGO_URI=mongodb+srv://your_database_url/

   DB_NAME=your_database_name
   ```

5. Navigate back to the src directory and install dependencies:
   ```bash
   cd ..
   pip install -r requirements.txt
   ```

6. Start the server:
   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000` and the Swagger documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the client directory:
   ```bash
   cd gaied-ctrl-alt-defeat/code/src/client
   ```

2. Install dependencies:
   ```bash
   npm i --force
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`.



## License

This project is licensed under the MIT License - see the LICENSE file for details.