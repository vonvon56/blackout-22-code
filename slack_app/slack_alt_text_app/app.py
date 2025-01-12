# import os
import json 
import requests
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
# from dotenv import load_dotenv

# Load .env file
# load_dotenv()

# Environment variables
# SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
# SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Initialize Slack app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# Flask app setup
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Handle Slack events
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # Event Subscription의 URL 검증(challenge) 때문에 필요한 경우:
    if request.headers.get("Content-Type") == "application/json":
        data = request.json
        if "challenge" in data:
            return jsonify({"challenge": data["challenge"]})
    
    # 그 외 경우는 Bolt에 그대로 넘기기
    return handler.handle(request)

# Listen for file_shared events
@app.event("file_shared")
def handle_file_shared(event, client):
    # Extract file info and channel info from the event
    file_id = event["file"]["id"]
    channel_id = event["channel_id"]

    # 파일 상세 정보 가져오기
    response = client.files_info(file=file_id)
    file_info = response["file"]
    file_name = file_info["name"]
    file_url = file_info["url_private"]
    type_ = event.get("type")
    user_id = event.get("user_id")
    file = event.get("file", {})
    event_ts = event.get("event_ts")
    channel_info = client.conversations_info(channel=channel_id)
    channel_name = channel_info["channel"]["name"]
    history = client.conversations_history(channel=channel_id, limit=10)  # 최근 10개 메시지 가져오기
    related_message = None
    if history and history["messages"]:
        for message in history["messages"]:
            # 메시지와 파일 타임스탬프가 근접한 경우
            if "files" in message and file_id in [f["id"] for f in message["files"]]:
                related_message = message.get("text", "메시지가 없습니다.")
                break
            
    # JSON 형식으로 버튼 value에 담을 문자열 만들기
    button_value = json.dumps({
        "file_name": file_name,
        "file_url": file_url,
        "type_": type_,
        "file_id": file_id,
        "user_id": user_id,
        "file": file,
        "channel_id": channel_id,
        "event_ts": event_ts,
        "message_text": related_message,
        "channel_name": channel_name,
    })

    # Post a message with a button
    client.chat_postMessage(
        channel=channel_id,
        text="A file has been uploaded!",
        blocks=[
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "대체텍스트 보기"
                        },
                        "action_id": "button_click",
                        "value": button_value,
                        "style": "primary"
                    }
                ]
            }
        ]
    )

# Handle button clicks
@app.action("button_click")
def handle_button_click(ack, body, say, client):
    ack()  # Acknowledge the button click

    # 버튼 value에 있던 JSON 문자열 꺼내기
    raw_value = body["actions"][0]["value"]

     # JSON 파싱
    import json
    data = json.loads(raw_value)
    file_name = data["file_name"]
    file_url = data["file_url"]
    type_ = data["type_"]
    file_id = data["file_id"]
    user_id = data["user_id"]
    file = data["file"]
    channel_id = data["channel_id"]
    event_ts = data["event_ts"]
    message_text = data["message_text"]
    channel_name = data["channel_name"]
    button_click_user_id = body["user"]["id"]

    generation_message = client.chat_postMessage(
        channel=button_click_user_id,  # 개인 DM으로 전송
        text=f"대체텍스트 생성 중..."
    )

     # 메시지의 ts 값 저장
    generation_message_ts = generation_message["ts"]

    payload1 = {
        "url_private": file_url
    }
    ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

    payload2 = {
        "type": type_,
        "file_id": file_id,
        "user_id": user_id,
        "file": {
            "id": file.get("id")
        },
        "channel_id": channel_id,
        "event_ts": event_ts
    }

    # Check if the file is an image
    if any(file_name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
      # for image
      aws_url = "https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/jpg"
      try:
        response = requests.post(aws_url, json=payload1, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
              alt_text = response.json().get("alt_text", "No alternative text found.")
               # (1) "대체텍스트 생성 중..." 메시지 삭제
              client.chat_delete(channel=button_click_user_id, ts=generation_message_ts)
              # (2) 새 메시지로 대체텍스트 전송
              client.chat_postMessage(
                  channel=button_click_user_id,  # 개인 DM으로 전송
                  blocks=[
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": f"다음은 채널 {channel_name}에 전송된 이미지 파일에 대한 대체텍스트입니다: {alt_text}"
                          }
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": f"다음은 파일과 함께 전달된 메시지입니다: {message_text}"
                          }
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": f"다음은 원본 파일의 이름과 링크입니다.{file_name}\n{file_url} 끝."
                          }
                      },
                  ]
              )
        else:
              client.chat_postMessage(
                  channel=button_click_user_id,  
                  text=f"Failed to retrieve file. Status Code: {response.status_code}, Response: {response.text}"
              )
      except requests.exceptions.RequestException as e:
        client.chat_postMessage(
                  channel=button_click_user_id,  
                  text=f"대체텍스트 생성 실패: {e}"
              )
        
    elif file_name.lower().endswith(".pdf"):
          
      aws_url2 = "https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf"
      try:
        response = requests.post(aws_url2, json=payload2, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
                summary = response.json().get("summary", "No summary found.")
                # (1) "대체텍스트 생성 중..." 메시지 삭제
                client.chat_delete(channel=button_click_user_id, ts=generation_message_ts)
                # (2) 새 메시지로 대체텍스트 전송
                client.chat_postMessage(
                    channel=button_click_user_id,  # 개인 DM으로 전송
                    blocks=[
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": f"다음은 채널 {channel_name}에 전송된 pdf 파일에 대한 대체텍스트 요약본입니다: {summary}"
                          }
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": f"다음은 파일과 함께 전달된 메시지입니다: {message_text}"
                          }
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": f"다음은 원본 파일의 이름과 링크입니다.{file_name}\n{file_url} 끝."
                          }
                      },
                  ]
                )
        else:
              client.chat_postMessage(
                  channel=button_click_user_id,  
                  text=f"Failed to retrieve file. Status Code: {response.status_code}, Response: {response.text}"
              )
      except requests.exceptions.RequestException as e:
        client.chat_postMessage(
                  channel=button_click_user_id,  
                  text=f"대체텍스트 생성 실패: {e}"
              )
     
    else:
        client.chat_postMessage(
                  channel=button_click_user_id,  
                  text=f"The attached file must be a PDF or image."
        )
        return

    
# Run Flask app
if __name__ == "__main__":
    flask_app.run(port=3000)