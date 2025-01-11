import json
import base64
import requests
import boto3

# Slack Bot User OAuth Token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# alttext.ai API 정보
ALT_TEXT_AI_URL = os.getenv("ALT_TEXT_AI_URL")
ALT_TEXT_AI_KEY = os.getenv("ALT_TEXT_AI_KEY") 

def lambda_handler(event, context):
    try:
        # 1) Slack 이벤트 파싱
        body = json.loads(event["body"])
        file_url = body["url_private"]
        print("File URL:", file_url)

        # 2) Slack 파일 다운로드
        image_bytes = download_image_from_slack(file_url)
        print("Downloaded image bytes:", len(image_bytes))

        # 3) alttext.ai 호출 (Base64 인코딩 방식)
        alt_text = get_alt_text_via_base64(image_bytes)
        print("alt_text from alttext.ai:", alt_text)

        # 4) 결과 반환
        return {
            "statusCode": 200,
            "body": json.dumps({"alt_text": alt_text})
        }

    except Exception as e:
        print("Error in lambda_handler:", e)
        return {
            "statusCode": 500,
            "body": str(e)
        }

def download_image_from_slack(file_url: str) -> bytes:
    """
    Slack 비공개 URL에서 이미지를 다운로드.
    """
    slack_headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    response = requests.get(file_url, headers=slack_headers)
    if response.status_code != 200:
        raise Exception(f"Failed to download image from Slack. Status code: {response.status_code}")

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        # 필요하다면 확장자별로 예외 처리
        raise Exception("Downloaded file is not recognized as an image.")

    return response.content

def get_alt_text_via_base64(image_bytes: bytes) -> str:
    """
    Base64 인코딩 방식으로 alttext.ai에 이미지를 업로드하고 alt_text를 반환.
    """
    # 1) Base64 인코딩
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    # 2) Request Body (url 필드 없음, raw 필드만)
    data = {
        "image": {
            "raw": b64_image
        }
    }

    # 3) Headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": ALT_TEXT_AI_KEY
    }

    # 4) POST 요청
    response = requests.post(ALT_TEXT_AI_URL, headers=headers, json=data)
    print("alttext.ai response:", response.status_code, response.text)

    if response.status_code == 200:
        resp_json = response.json()
        alt_text = resp_json.get("alt_text")
        if alt_text:
            return alt_text
        else:
            raise ValueError("No alt_text returned from alttext.ai")
    else:
        raise RuntimeError(
            f"alttext.ai request failed with status code {response.status_code}, "
            f"response body: {response.text}"
        )