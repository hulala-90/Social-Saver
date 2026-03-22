🧱 SOCIAL SAVER
Mine Your Knowledge ⚒️ | AI-Powered WhatsApp Research Vault

Social Saver is an AI-native knowledge mining system that turns WhatsApp into a powerful research assistant.

Built with a Minecraft-inspired UI theme, it allows users to send links or images directly via WhatsApp and automatically:

🧠 Extract insights
✨ Generate AI summaries
🏷 Auto-tag content
📦 Store everything in a searchable dashboard
🚀 Live Demo

🌍 Deployed on Render
📲 WhatsApp Integration via Twilio Sandbox

⚠️ Note: Currently running on Twilio Sandbox (users must join sandbox during testing). In production, this would use the official WhatsApp Business API.

🎯 Problem Statement

Students, researchers, and creators constantly find valuable information across:

Instagram reels
News apps
Blog posts
Twitter threads
Screenshots

But:

Links get buried in chats
Screenshots become unsearchable
No structured organization
No instant summaries

Social Saver solves this by turning WhatsApp into a structured AI-powered knowledge vault.

⚔️ Core Features
📲 1. WhatsApp-Based Input

Users send:

A URL
A screenshot
A media file

Directly to the bot.

🧠 2. AI Content Mining (Gemini Powered)

Using Google Gemini API, the system:

Generates 1-line smart summaries
Extracts meaningful keywords
Assigns intelligent tags (#Coding, #Finance, #News, etc.)
🔍 3. OCR + Research Link Extraction

If an image is sent:

OCR extracts headline
AI understands context
“Find Article” search link is generated
🗄 4. Knowledge Vault Dashboard

Minecraft-inspired UI with:

🔎 Search functionality
🏷 Tag filtering
🎲 Surprise Me (random resurfacing)
❌ Delete entries
📦 Card-based knowledge blocks
🎮 5. Gamified UI Theme

Custom-designed Minecraft-style interface:

Pixel fonts
Block borders
Inventory grid layout
Nether portal CTA
Crafting process visual storytelling
🛠️ Tech Stack
Backend
⚡ FastAPI
🐍 Python
AI
🤖 Google Gemini API
Database
🍃 MongoDB Atlas (NoSQL)
Messaging
📲 Twilio WhatsApp API (Sandbox Mode)
Frontend
🎨 HTML5
🧱 TailwindCSS
🖼 Jinja2 Templates
Deployment
☁️ Render (Cloud Hosting)
🏗 System Architecture
User → WhatsApp → Twilio Webhook → FastAPI
        ↓
   Content Extraction
        ↓
    Gemini AI Processing
        ↓
    MongoDB Storage
        ↓
   Dashboard Retrieval
📂 Project Structure
Social-Saver/
│
├── main.py
├── templates/
│   ├── index.html
│   └── dashboard.html
├── static/
├── requirements.txt
├── .env
└── README.md
⚙️ Local Setup Guide
1️⃣ Clone Repository
git clone https://github.com/hulala-90/Social-Saver.git
cd Social-Saver
2️⃣ Create Virtual Environment
python -m venv venv

Activate:

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Create .env File
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=your_twilio_number

GEMINI_API_KEY=your_gemini_api_key

MONGO_URI=your_mongodb_atlas_uri

BASE_URL=https://your-render-url.onrender.com
5️⃣ Run Locally
uvicorn main:app --reload
🌐 Deployment (Render)
Connected GitHub repo

Build Command:

pip install -r requirements.txt

Start Command:

uvicorn main:app --host 0.0.0.0 --port 10000
🔐 Security Practices
All API keys stored in environment variables
.env excluded via .gitignore
MongoDB Atlas IP whitelisting enabled
No hardcoded secrets in code
🧠 Engineering Decisions
Why MongoDB?

Flexible schema allows:

Dynamic tag storage
Future feature expansion
Multimodal data storage
Why FastAPI?
Async support
Fast webhook handling
Clean API structure
Why WhatsApp?
Zero friction
No new app required
High daily usage platform
🧪 Current Limitation (Sandbox Mode)

Users must send:

join <sandbox-name>

To activate the bot.

In production:

WhatsApp Business API removes this requirement.
🚀 Future Improvements
User authentication system
Tag-based filtering UI
AI-powered semantic search
Vector embeddings for deep search
WhatsApp interactive buttons
Multi-language support
🏆 Hackathon Build

Built for SPIT Hackathon
Designed to demonstrate:

AI integration
Real-world messaging workflows
Cloud deployment
Full-stack development
Product thinking
👨‍💻 Developed By

Darshan Yadav

AI + Backend + Full Stack Enthusiast
Building intelligent systems that feel magical ⚡
