# 🧠 Social Saver: AI-Native Research Assistant

**Social Saver** is an intelligent knowledge-management tool built for the SPIT Hackathon. It allows users to save, summarize, and categorize information from web links (Instagram reels, blogs, articles) or physical media (news screenshots) directly through WhatsApp.

---

## 🚀 The Problem
Students and researchers often find valuable information on social media or news apps but struggle to organize it. Saving links manually is tedious, and screenshots often get "lost" in phone galleries without being searchable or summarized.

## ✨ Key Features
* **Multimodal Input**: Send a URL or a Screenshot directly via WhatsApp.
* **AI Summarization**: Leverages **Gemini 2.5 Flash** to provide instant 1-sentence summaries of long articles or messy social media data.
* **Intelligent OCR & Search**: Extracts headlines from news images and provides a "Find Article" search link for deeper research.
* **Automated Categorization**: AI assigns tags (e.g., #Coding, #Finance, #News) automatically based on content.
* **Dynamic Dashboard**: A responsive web UI to search, filter by category, and manage your saved research library.

## 🛠️ Tech Stack
* **Backend**: FastAPI (Python)
* **Generative AI**: Google Gemini 2.5 Flash API
* **Database**: MongoDB Atlas (NoSQL)
* **Messaging**: Twilio WhatsApp API
* **Deployment/Tunneling**: Ngrok
* **Frontend**: HTML5, Bootstrap 5, Jinja2 Templates

## 🏗️ Architecture
1.  **Input**: User sends a link or image to the Twilio WhatsApp Sandbox.
2.  **Processing**: FastAPI receives the webhook, downloads media using authenticated requests, and sends the raw content/bytes to Gemini.
3.  **Storage**: Extracted metadata (URL, Tag, Summary) is stored in a MongoDB Atlas cluster.
4.  **Consumption**: Users access their organized "Knowledge Cards" via a searchable web dashboard.

## ⚙️ Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/hulala-90/Social-Saver.git](https://github.com/hulala-90/Social-Saver.git)
    cd Social-Saver
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Mac/Linux
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**: Create a `.env` file in the root directory:
    ```text
    TWILIO_SID=your_twilio_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    GEMINI_API_KEY=your_google_ai_key
    MONGO_URI=your_mongodb_atlas_uri
    RAPIDAPI_KEY=your_rapidapi_key
    NGROK_URL=your_active_ngrok_url
    ```

5.  **Run the application**:
    ```bash
    uvicorn main:app --reload
    ```

## 📜 Evaluation Criteria & Best Practices
* **Security**: API keys are managed via environment variables and excluded from version control using `.gitignore`.
* **Scalability**: Uses NoSQL (MongoDB) for flexible data schema as research categories evolve.
* **UX**: Integrated "Surprise Me" feature to resurface old research and "Delete" functionality for library maintenance.

---
**Developed by Darshan Yadav**
