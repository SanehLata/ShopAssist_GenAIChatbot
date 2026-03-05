# ShopAssist_GenAIChatbot
The project implements an intelligent, e-commerce chatbot powered by semantic routing workflow designed to deliver accurate, context-aware assistance. The chatbot analyze user intent and dynamically route queries to the appropriate processing pipeline, enabling efficient handling of FAQs, product information requests, and URL queries.

### ▶️ Running the Chatbot
https://shop-assist-gen-ai-chatbot.streamlit.app/

### Architecture Diagram

![Architecture Diagram](docs/architecture.jpg)

## 🚀 Features

- 💬 **Smart Intent Understanding** — Routes questions to the correct processing logic.
- 🛍️ **E‑commerce Focused** — Designed for online store interactions.
- 🧠 **Context‑Aware Responses** — Improves accuracy and relevance.
- 🔄 **Semantic Routing Workflow** — Efficient pipeline for natural language queries.
- 📦 **Uses Python & AI Libraries** — Easily extendable and customizable.


### ⚙️ Installation

Clone the repo

git clone https://github.com/SanehLata/ShopAssist_GenAIChatbot.git
cd ShopAssist_GenAIChatbot

Create a virtual environment

python3 -m venv venv
source venv/bin/activate    # macOS & Linux
# OR
venv\Scripts\activate       # Windows

Install dependencies

pip install -r requirements.txt


### 🛠️ Tech Stack
#### 1. Programming & Frameworks

  Python 3.10+ – Core language for backend and AI integration

  Streamlit – Frontend UI for running the chatbot locally or online

#### 2. AI & NLP

  Groq model(llama-3.1-8b-instant) – For natural language understanding and response generation

  HuggingFace Transformers – Alternative LLM embeddings and encoders

  Semantic Search / Vector Database – Chroma for knowledge retrieval 

  Embedding Model (all-MiniLM-L6-v2) to generate Text embeddings for semantic similarity search

#### 3. Database & Storage

  SQLite for storing product data

  CSV – Knowledge base storage for FAQs

