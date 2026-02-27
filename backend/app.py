from duckduckgo_search import DDGS
import os
import re
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Import the NEW google genai library
from google import genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Securely fetch API keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_dynamic_prerequisites(topic):
    """Uses Google Gemini to dynamically generate prerequisites for ANY topic."""
    if not GEMINI_API_KEY:
        return ["Basic Computer Knowledge (No API Key)"]

    try:
        # Initialize the new Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"List exactly 3 short, essential prerequisites needed before learning '{topic}'. Return ONLY a comma-separated list. No introduction, no bullet points, no extra text."

        # New generation syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        text_result = response.text.strip()
        prereqs = [p.strip() for p in text_result.split(',') if p.strip()]

        return prereqs[:3] if prereqs else ["Basic Computer Knowledge"]


    except Exception as e:

        print(f"Gemini API Error: {e}")

        # Change this line so the error shows up on the frontend!

        return [f"API Error: {str(e)}"]


def classify_duration(minutes):
    if minutes < 10:
        return "short"
    elif minutes <= 30:
        return "medium"
    return "long"


def parse_youtube_duration(duration_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    return (hours * 60) + minutes


def fetch_youtube_videos(topic, prereqs_list):
    videos = []
    if not YOUTUBE_API_KEY: return videos

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        search_request = youtube.search().list(q=topic + " tutorial", part="id", type="video", maxResults=6)
        search_response = search_request.execute()

        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        if not video_ids: return videos

        video_request = youtube.videos().list(part="snippet,contentDetails", id=",".join(video_ids))
        video_response = video_request.execute()

        for item in video_response.get("items", []):
            duration_str = item["contentDetails"]["duration"]
            total_minutes = parse_youtube_duration(duration_str)

            videos.append({
                "title": item["snippet"]["title"],
                "link": f"https://www.youtube.com/watch?v={item['id']}",
                "platform": "youtube",
                "duration": classify_duration(total_minutes),
                "cost": "free",
                "prerequisites": prereqs_list
            })
    except HttpError as e:
        print(f"YouTube API Error: {e}")
    return videos


def fetch_articles(topic, prereqs_list):
    articles = []

    # We use your existing YouTube API key, because it works for all Google APIs!
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

    if not API_KEY or not SEARCH_ENGINE_ID:
        print("Missing Google Search API Key or Engine ID")
        return articles

    try:
        # The official Google Custom Search API URL
        url = f"https://www.googleapis.com/customsearch/v1?q={topic}+tutorial+geeksforgeeks&key={API_KEY}&cx={SEARCH_ENGINE_ID}&num=5"

        response = requests.get(url)
        data = response.json()

        # Extract the results from the official JSON response
        if "items" in data:
            for item in data["items"]:
                articles.append({
                    "title": item["title"],
                    "link": item["link"],
                    "platform": "website",
                    "duration": "medium",
                    "cost": "free",
                    "prerequisites": prereqs_list
                })

    except Exception as e:
        print(f"Official Google Search Error: {e}")

    return articles
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results")
def results():
    topic = request.args.get("topic")
    resources = []

    if topic:
        dynamic_prereqs = get_dynamic_prerequisites(topic)
        yt_resources = fetch_youtube_videos(topic, dynamic_prereqs)
        web_resources = fetch_articles(topic, dynamic_prereqs)
        resources = yt_resources + web_resources

    return render_template(
        "results.html",
        topic=topic,
        resources=resources
    )


if __name__ == "__main__":
    app.run(debug=True)