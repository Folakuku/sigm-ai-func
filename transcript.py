import requests
import re
import os
import re
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TRANSCRIPT_API_KEY = os.getenv("YOUTUBE_TRANSCRIPT_KEY")


def get_transcript_from_id(video_id: str) -> dict:
    headers = {
        "Authorization": f"Basic {TRANSCRIPT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"ids": [video_id]}
    transcript_url = "https://www.youtube-transcript.io/api/transcripts"

    transcript_response = requests.post(
        transcript_url, headers=headers, json=payload)

    transcript_data = transcript_response.json()

    transcript_segments = transcript_data[0]["tracks"][0]['transcript']
    transcript_text = " ".join(segment["text"]
                               for segment in transcript_segments)

    return transcript_text


def extract_video_id(video_url: str) -> str:
    """Extracts the video ID from a YouTube URL safely."""
    match = re.search(
        r"(?:v=|\/embed\/|\/v\/|youtu\.be\/|\/e\/|watch\?v=)([^#\&\?]+)", video_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")


def get_transcript_from_url(video_url: str) -> dict:
    """Fetches the transcript for a given YouTube video URL."""
    try:
        if not TRANSCRIPT_API_KEY:
            raise ValueError(
                "Missing YOUTUBE_TRANSCRIPT_KEY in environment variables.")

        video_id = extract_video_id(video_url)
        headers = {
            "Authorization": f"Basic {TRANSCRIPT_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"ids": [video_id]}
        transcript_url = "https://www.youtube-transcript.io/api/transcripts"

        response = requests.post(transcript_url, headers=headers, json=payload)

        if response.status_code != 200:
            raise ValueError(
                f"Failed to fetch transcript. Status Code: {response.status_code}, Response: {response.text}")

        transcript_data = response.json()

        # Validate API response structure
        if not transcript_data or "tracks" not in transcript_data[0]:
            raise ValueError("Unexpected transcript API response format.")

        transcript_segments = transcript_data[0]["tracks"][0].get(
            "transcript", [])
        transcript_text = " ".join(segment.get("text", "")
                                   for segment in transcript_segments)

        return {"transcript": transcript_text}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
