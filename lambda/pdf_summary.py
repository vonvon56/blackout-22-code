import json
import os
import tempfile
import requests
import fitz  # PyMuPDF
import openai

# OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Slack API 토큰 설정 (환경 변수에서 가져오기)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

def lambda_handler(event, context):
    try:
        # 1) Slack 이벤트 데이터에서 file_id 추출
        body = json.loads(event["body"])
        file_id = body.get("file_id")
        if not file_id:
            raise ValueError("Missing file_id in the event data.")

        # 2) Slack API를 사용해 파일 정보 가져오기
        file_info_url = f"https://slack.com/api/files.info?file={file_id}"
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

        response = requests.get(file_info_url, headers=headers)
        file_info = response.json()
        if not file_info.get("ok"):
            print(f"Slack API Response: {response.status_code}, {response.text}")
            raise ValueError(f"Failed to fetch file info: {file_info.get('error')}")

        file_url = file_info["file"].get("url_private")
        file_name = file_info["file"].get("name")
        if not file_url or not file_name:
            raise ValueError("File URL or name is missing from the response.")

        # 3) 파일 다운로드
        temp_dir = tempfile.gettempdir()
        local_file_path = os.path.join(temp_dir, file_name)

        download_response = requests.get(file_url, headers=headers, stream=True)
        if download_response.status_code != 200:
            raise ValueError("Failed to download file from Slack")

        with open(local_file_path, "wb") as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("PDF downloaded successfully.")

        # 4) fitz(PyMuPDF)로 PDF 텍스트 추출
        doc = fitz.open(local_file_path)
        extracted_text = ""

        # 첫 2페이지만 텍스트 추출
        for page_idx in range(min(2, len(doc))):
            page = doc[page_idx]
            extracted_text += page.get_text()

        doc.close()
        print("Extracted Text via fitz:", extracted_text)

        # 5) OpenAI API를 사용한 텍스트 요약
        if len(extracted_text) > 4000:
            extracted_text = extracted_text[:4000]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following text in Korean. The result should be one or two sentences that includes the most important part of the file.\n\n{extracted_text}"}
            ]
        )
        summary = response.choices[0].message.content
        print("Summary:", summary)

        # 6) 결과 반환
        return {
            "statusCode": 200,
            "body": json.dumps({
                "summary": summary,
            })
        }

    except requests.exceptions.RequestException as req_err:
        print("RequestException in lambda_handler:", req_err)
        return {
            "statusCode": 500,
            "body": "Failed to connect to Slack or OpenAI API."
        }
    except Exception as e:
        print("Error in lambda_handler:", e)
        return {
            "statusCode": 500,
            "body": str(e)
        }
