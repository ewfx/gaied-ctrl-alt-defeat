## 📌 Table of Contents

- [Introduction](Introduction)

- [Demo](Demo)

- [Inspiration](Inspiration)

- [What It Does](What-it-does)

- [How We Built It](How-we-built-it)

- [Challenges We Faced](Challenges-we-faced)

- [How to Run](How-to-run)

- [Tech Stack](Tech-stack)

- [Team](Team)

---
## 🎯 Introduction

### Email Classification System

A powerful API for automatically classifying commercial bank lending service emails and extracting relevant information for service requests with duplicate check and sending the requests to specific support group based on the content of the request.

## 🎥 Demo

🔗 [Live Demo](#) (if applicable)

📹 [Video Demo](#) (if applicable)
  
🖼️ Screenshots:
### Overall detailed flow

![Overall detailed flow](artifacts/arch/detailed_flow.png)

### UI Landing page

![UI landing page](artifacts/demo/Images/front_UI.jpeg)

### Upload files page

![upload files page](artifacts/demo/Images/upload_files_pdf.jpeg)

### Configure page

![configure page](artifacts/demo/Images/configure_request_types.jpeg)

### Analytics page

![analysis page](artifacts/demo/Images/analysis_diagrams.jpeg)

### Analytics page recent requests

![analysis page_recent_requests](artifacts/demo/Images/recent_requests.jpeg)






## 💡 Inspiration
The inspiration for this project stemmed from the growing need to efficiently process and analyze large volumes of unstructured information, such as emails and attachments. We recognized that businesses and individuals often struggle with retrieving relevant data quickly, especially when dealing with redundant content and scattered information.

With advancements in LLMs (Large Language Models) and embeddings, we saw an opportunity to build an intelligent system that could streamline this process. Our goal was to leverage Gemma 2.9B and all-MiniLM-L6-v2 embeddings to create a solution that not only retrieves relevant documents but also understands context, enabling users to find insights effortlessly.

We also wanted to ensure that our system was scalable, efficient, and user-friendly, which led us to choose a modern stack: Next.js + ShadCN for the frontend, FastAPI + LangChain for the backend, and MongoDB for data storage. These technologies allowed us to build an interactive and seamless experience while maintaining high performance.

Ultimately, this project was driven by our passion for AI-powered solutions and our desire to simplify information retrieval, making knowledge more accessible and actionable.


## ⚙️ What It Does
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


  

## 🛠️ How We Built It

We built this project using a modern tech stack to ensure scalability, efficiency, and a smooth user experience.

• **Frontend:** We used **NextJS** with **ShadCN/UI** for a responsive and aesthetically pleasing user interface. Next.js provides server-side rendering (SSR) and static site generation (SSG) for optimal performance, while ShadCN/UI offers pre-built, customizable components for a seamless user experience.

• **Backend:** The backend is powered by **FastAPI**, a high-performance Python framework that enables fast API development with automatic documentation. We integrated **LangChain** to manage LLM interactions efficiently, allowing structured and dynamic responses from the language model.

• **Database:** We chose **MongoDB** as our database due to its flexible document-based storage, which is well-suited for handling AI-generated content and embeddings.

• **LLM Model:** We leveraged **Gemma 2.9B**, a lightweight yet powerful open-weight large language model, optimized for efficient text generation and reasoning tasks.

• **Embeddings:** We utilized **all-MiniLM-L6-v2** for embeddings, ensuring fast and efficient text similarity searches, enabling the system to retrieve and process relevant information quickly.

  This stack allowed us to build a responsive, AI-powered application that seamlessly integrates natural language processing with a robust and scalable architecture.

  

## 🚧 Challenges We Faced

Building this project came with several challenges that required careful consideration and problem-solving:

• **Handling Various Scenarios of Duplicate Emails and Attachments:** One of the key challenges was ensuring that duplicate emails and attachments were properly managed. Since users could upload the same files multiple times, we had to implement efficient deduplication techniques. This involved checking for content similarity using embeddings and designing a system that could distinguish between intentional re-uploads and accidental duplicates while maintaining data integrity.

• **Choosing the Right LLM:** Selecting the most suitable language model was another critical decision. We needed a model that balanced accuracy, performance, and cost-efficiency. After evaluating multiple options, we settled on **Gemma 2.9B**, which provided strong natural language understanding capabilities without excessive computational overhead. However, fine-tuning and integrating it with **LangChain** required testing different configurations to optimize response quality.

• **Deciding the Tradeoff Between Efficiency and Speed:** Optimizing for both speed and efficiency was a constant balancing act. While larger models offer better accuracy, they come with increased latency. We had to ensure that the application delivered quick responses without compromising on the quality of results. Techniques like caching, embedding-based retrieval, and optimizing API calls helped us achieve this balance.

• **Working Within a Limited Timeframe:** Given the constraints of time, we had to make strategic decisions on prioritization. Some features had to be scoped down, and we relied on iterative development to quickly test and refine the core functionality. Efficient collaboration, leveraging pre-built solutions like **ShadCN/UI** for the frontend and **FastAPI** for the backend, helped accelerate development.

  

Despite these challenges, we successfully built a robust and scalable system by making thoughtful trade-offs and optimizing our approach at each stage.

  

## 🏃 How to Run
  

## Setup Instructions

  

### Prerequisites

  

- Python 3.10 or higher

- Node.js 18.0 or higher

- API keys for LLM services (if applicable)

  

### Backend Setup

  

1. Create a virtual environment:

```bash

python -m venv hackathon

source hackathon/bin/activate # On Windows: hackathon\Scripts\activate

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

  

## 🏗️ Tech Stack

- 🔹 Frontend: NextJS / ShadCN

- 🔹 Backend: FastAPI, Langchain

- 🔹 Database: MongoDB

- 🔹 Other: all-MiniLM-L6-v2 - embeddings

  

## 👥 Team

- Amith G - [GitHub](https://github.com/amyyyth) | [LinkedIn](https://www.linkedin.com/in/amith-g-95abb5207)

- Bhanu - [GitHub](https://github.com/BhanuPrakashPebbeti) | [LinkedIn](https://www.linkedin.com/in/bhanu-prakash-pebbeti-700b80191/)

- Hilmi Parveen - [GitHub](https://github.com/hilmiparveen) | [LinkedIn](https://www.linkedin.com/in/hilmi-parveen/)

