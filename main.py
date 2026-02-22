import os
import re
import json
import random
import datetime
import requests
from bson import ObjectId
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from twilio.twiml.messaging_response import MessagingResponse
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv

# --- 1. SETUP: LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
MONGO_URI = os.getenv("MONGO_URI")
NGROK_URL = os.getenv("NGROK_URL")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. DATABASE CONFIGURATION ---
client = MongoClient(MONGO_URI)
db = client['social_saver_db']
saves_collection = db['saves']

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- 3. DATABASE HELPER ---
def save_to_mongo(url, tag, summary):
    document = {
        "url": url,
        "tag": tag,
        "summary": summary,
        "timestamp": datetime.datetime.utcnow()
    }
    saves_collection.insert_one(document)
    print(f"✅ Document saved to MongoDB: {tag}")

# --- 4. EXTRACTION & AI ENGINE ---
def extract_text_from_url(url):
    if "instagram.com" in url:
        try:
            match = re.search(r'/(?:p|reel)/([^/?]+)', url)
            if not match: return "Invalid Instagram URL."
            shortcode = match.group(1)
            
            api_url = "https://instagram-best-experience.p.rapidapi.com/post"
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "instagram-best-experience.p.rapidapi.com"
            }
            response = requests.get(api_url, headers=headers, params={"shortcode": shortcode}, timeout=10)
            return str(response.json())[:15000]
        except Exception:
            return "Instagram content extracted via metadata fallback."
    else:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.title.string if soup.title else "Unknown Title"
            content = ' '.join([p.text for p in soup.find_all('p')[:3]])
            return f"Title: {title}. Content: {content}"
        except:
            return "Could not read website content."

def analyze_content(text_content):
    prompt = f"""
    Analyze this content. 
    1. Categorize into a one-word tag (e.g., 'Coding', 'Fitness', 'Food').
    2. Write a 1-sentence summary.
    Return ONLY a valid JSON object: {{"tag": "Category", "summary": "Summary text"}}
    Data: {text_content}
    """
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.strip().lstrip('```json').rstrip('```').strip()
        data = json.loads(clean_text)
        return data['tag'], data['summary']
    except Exception as e:
        print(f"AI Link Error: {e}")
        return "Misc", "Saved, but AI summary failed."

# --- 5. DASHBOARD ROUTES ---
@app.get("/dashboard")
async def get_dashboard(request: Request, search: str = None, tag_filter: str = None, random_pick: bool = False):
    unique_tags = saves_collection.distinct("tag")
    query = {}
    
    if search:
        query = {"$or": [
            {"summary": {"$regex": search, "$options": "i"}},
            {"tag": {"$regex": search, "$options": "i"}}
        ]}
    elif tag_filter:
        query = {"tag": tag_filter}

    if random_pick:
        all_matches = list(saves_collection.find(query))
        items = [random.choice(all_matches)] if all_matches else []
    else:
        items = list(saves_collection.find(query).sort("timestamp", -1))
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "items": items, 
        "tags": unique_tags,
        "active_tag": tag_filter
    })

# --- THE MISSING DELETE ROUTE ---
@app.post("/delete/{item_id}")
async def delete_item(item_id: str):
    # Converts the string ID from the URL into a MongoDB ObjectId
    saves_collection.delete_one({"_id": ObjectId(item_id)})
    # Redirects back to the dashboard after deletion
    return Response(status_code=303, headers={"Location": "/dashboard"})

# --- 6. WHATSAPP WEBHOOK ---
@app.post("/whatsapp")
async def reply_whatsapp(
    Body: str = Form(default=""), 
    From: str = Form(default=""),
    MediaUrl0: str = Form(default=None) 
):
    response = MessagingResponse()
    
    # CASE 1: HANDLE IMAGE INPUT (OCR to Search URL)
    if MediaUrl0:
        print(f"📸 Authenticating and downloading image...")
        try:
            img_res = requests.get(
                MediaUrl0, 
                auth=HTTPBasicAuth(TWILIO_SID, TWILIO_AUTH_TOKEN),
                timeout=15
            )
            
            if img_res.status_code == 200:
                vision_res = model.generate_content([
                    """Analyze this image. 
                    1. Extract the main headline or core topic text.
                    2. Identify the news source name if visible.
                    Return ONLY JSON: {'tag': 'Category', 'summary': '1-sentence summary', 'headline': 'full headline'}""",
                    {"mime_type": "image/jpeg", "data": img_res.content}
                ])
                
                clean_text = vision_res.text.strip().lstrip('```json').rstrip('```').strip()
                data = json.loads(clean_text)
                
                tag = data.get('tag', 'Image')
                summary = data.get('summary', 'Visual content saved.')
                headline = data.get('headline', 'News Article')
                
                search_url = f"https://www.google.com/search?q={headline.replace(' ', '+')}"
                save_to_mongo(search_url, tag, summary)
                reply = f"📸 Analyzed! Saved to '{tag}'.\n\nSummary: {summary}"
            else:
                reply = "❌ Twilio download failed. Verify Auth Token."
        except Exception as e:
            print(f"Vision Error: {e}")
            reply = "❌ Could not process image. Try a clearer screenshot."

    # CASE 2: HANDLE LINKS
    else:
        url = Body.strip()
        scraped_text = extract_text_from_url(url)
        tag, summary = analyze_content(scraped_text)
        save_to_mongo(url, tag, summary)
        
        reply = f"✅ Saved to '{tag}'!\nSummary: {summary}\nView: {NGROK_URL}/dashboard"

    response.message(reply)
    return Response(content=str(response), media_type="application/xml")