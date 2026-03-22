import os
import re
import json
import random
import datetime
import requests
from fastapi.responses import HTMLResponse
from bson import ObjectId
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from twilio.twiml.messaging_response import MessagingResponse
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv


# -------------------- 1. LOAD ENV --------------------

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
MONGO_URI = os.getenv("MONGO_URI")
NGROK_URL = os.getenv("NGROK_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------- 2. DATABASE --------------------

client = MongoClient(MONGO_URI)
db = client["social_saver_db"]
saves_collection = db["saves"]

# Create indexes for performance (important)
saves_collection.create_index("user_phone")
saves_collection.create_index("tag")
saves_collection.create_index("timestamp")


# -------------------- 3. FASTAPI --------------------

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# -------------------- 4. DATABASE HELPER --------------------

def save_to_mongo(url, tag, summary, user_phone):
    document = {
        "user_phone": user_phone,
        "url": url,
        "tag": tag,
        "summary": summary,
        "timestamp": datetime.datetime.utcnow()
    }
    saves_collection.insert_one(document)


# -------------------- 5. CONTENT EXTRACTION --------------------

def extract_text_from_url(url):
    if "instagram.com" in url:
        try:
            match = re.search(r'/(?:p|reel)/([^/?]+)', url)
            if not match:
                return "Invalid Instagram URL."

            shortcode = match.group(1)

            api_url = "https://instagram-best-experience.p.rapidapi.com/post"
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "instagram-best-experience.p.rapidapi.com"
            }

            response = requests.get(
                api_url,
                headers=headers,
                params={"shortcode": shortcode},
                timeout=10
            )

            return str(response.json())[:15000]

        except Exception:
            return "Instagram content extracted via fallback."

    else:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")

            title = soup.title.string if soup.title else "Unknown Title"
            content = " ".join([p.text for p in soup.find_all("p")[:5]])

            return f"Title: {title}. Content: {content}"

        except Exception:
            return "Could not read website content."


def analyze_content(text_content):
    prompt = f"""
    Analyze this content.
    1. Categorize into a one-word tag (e.g., Coding, Fitness, Food).
    2. Write a 1-sentence summary.
    Return ONLY JSON:
    {{"tag": "Category", "summary": "Summary text"}}
    Data: {text_content}
    """

    try:
        response = model.generate_content(prompt)
        clean = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean)
        return data["tag"], data["summary"]

    except Exception:
        return "Misc", "Saved, but AI summary failed."


#------------------LANDING-PAGE----------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------- 6. DASHBOARD --------------------

@app.get("/dashboard/{phone}")
async def dashboard(
    request: Request,
    phone: str,
    search: str = None,
    tag_filter: str = None,
    random_pick: bool = False
):

    query = {"user_phone": phone}

    if search:
        query["$or"] = [
            {"summary": {"$regex": search, "$options": "i"}},
            {"tag": {"$regex": search, "$options": "i"}}
        ]

    if tag_filter:
        query["tag"] = tag_filter

    if random_pick:
        matches = list(saves_collection.find(query))
        items = [random.choice(matches)] if matches else []
    else:
        items = list(
            saves_collection.find(query).sort("timestamp", -1)
        )

    tags = saves_collection.distinct("tag", {"user_phone": phone})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "items": items,
        "tags": tags,
        "phone": phone
    })


# -------------------- 7. DELETE ROUTE --------------------

@app.post("/delete/{item_id}")
async def delete_item(item_id: str, request: Request):
    saves_collection.delete_one({"_id": ObjectId(item_id)})
    return RedirectResponse(
        request.headers.get("referer", "/"),
        status_code=303
    )


# -------------------- 8. WHATSAPP WEBHOOK --------------------

@app.post("/whatsapp")
async def reply_whatsapp(
    Body: str = Form(default=""),
    From: str = Form(default=""),
    MediaUrl0: str = Form(default=None)
):

    response = MessagingResponse()

    # -------- CASE 1: IMAGE --------
    if MediaUrl0:
        try:
            img_res = requests.get(
                MediaUrl0,
                auth=HTTPBasicAuth(TWILIO_SID, TWILIO_AUTH_TOKEN),
                timeout=15
            )

            if img_res.status_code == 200:

                vision_res = model.generate_content([
                    """Analyze this image.
                    Return ONLY JSON:
                    {"tag":"Category","summary":"1 sentence","headline":"headline"}""",
                    {"mime_type": "image/jpeg", "data": img_res.content}
                ])

                clean = vision_res.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(clean)

                tag = data.get("tag", "Image")
                summary = data.get("summary", "Visual content saved.")
                headline = data.get("headline", "News")

                search_url = f"https://www.google.com/search?q={headline.replace(' ', '+')}"

                save_to_mongo(search_url, tag, summary, From)

                reply = f"📸 Saved to '{tag}'!\nSummary: {summary}\nView: {NGROK_URL}/dashboard/{From}"

            else:
                reply = "❌ Failed to download image."

        except Exception:
            reply = "❌ Could not process image."

    # -------- CASE 2: LINK --------
    else:

        url = Body.strip()

        if not url.startswith("http"):
            response.message("Please send a valid link.")
            return Response(content=str(response), media_type="application/xml")

        scraped_text = extract_text_from_url(url)
        tag, summary = analyze_content(scraped_text)

        save_to_mongo(url, tag, summary, From)

        reply = f"✅ Saved to '{tag}'!\nSummary: {summary}\nView: {NGROK_URL}/dashboard/{From}"

    response.message(reply)
    return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))