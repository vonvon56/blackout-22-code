import os
import json 
import requests
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
from slack_sdk import WebClient

# Load .env file
load_dotenv()

# Environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")

# Initialize Slack app
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# Flask app setup
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

YOUR_USER_ID = "U086W6R17TL"

# Handle Slack events
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # Event Subscription의 URL 검증(challenge) 때문에 필요한 경우:
    if request.headers.get("Content-Type") == "application/json":
        data = request.json
        if "challenge" in data:
            return jsonify({"challenge": data["challenge"]})
    
    # 그 외 경우는 Bolt에 그대로 넘기기ds
    return handler.handle(request)

@app.message("hello")
def say_hello(message, say):
    say("Hello back!")

@app.event("message")
def handle_message_event(event, client, say):
    client = WebClient(token=SLACK_USER_TOKEN)
    # Ignore bot messages
    if event.get("bot_id"):
        return
    
    # Only process messages sent by you
    if event.get("user") != YOUR_USER_ID:
        return

    # Extract message details
    message_text = event.get("text", "").strip()
    channel_id = event["channel"]
    ts = event["ts"]

    # Prepare payload for typo correction API
    payload = {"text": message_text}
    url = "https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/typocorrect"

    try:
        # Call the typo correction API
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        corrected_text = response.json().get("corrected_message")

        if corrected_text.strip(".") != message_text:
          #say("corrected message: " + corrected_text)

          response = client.chat_update(
            channel=channel_id,
            ts=ts,
            text=corrected_text
        )
    except requests.exceptions.RequestException as e:
        # If correction fails, send a message in the thread
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=ts,
            text=f"문장 교정 실패: {str(e)}"
        )

    
# Run Flask app
if __name__ == "__main__":
    flask_app.run(port=3000)