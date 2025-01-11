import boto3
import json
import os
import tempfile

import fitz  # PyMuPDF
import openai

# OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv("OPENAI_API_KEY")

def lambda_handler(event, context):
    # 1) 이벤트(JSON) 파싱
    print("Received event:", event)
    print("openai version: ", openai.__version__)
    try:
        body = json.loads(event['body'])  # JSON 문자열 -> Python 딕셔너리
        bucket_name = body['bucket_name']
        file_name = body['file_name']
    except KeyError as e:
        print(f"KeyError: {e}")
        return {
            "statusCode": 400,
            "body": f"Missing key: {str(e)}"
        }
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return {
            "statusCode": 400,
            "body": f"Invalid JSON format: {str(e)}"
        }

    # 2) S3에서 PDF 다운로드
    s3_client = boto3.client('s3')
    temp_dir = tempfile.gettempdir()
    local_file_path = os.path.join(temp_dir, "input.pdf")

    try:
        s3_client.download_file(bucket_name, file_name, local_file_path)
        print("PDF downloaded successfully.")
    except Exception as e:
        print(f"Error downloading PDF from S3: {e}")
        return {
            "statusCode": 500,
            "body": f"Error downloading PDF: {str(e)}"
        }

    # 3) fitz(PyMuPDF)로 첫 두 페이지 텍스트 추출
    try:
        doc = fitz.open(local_file_path)
        extracted_text = ""

        # 첫 2페이지만 텍스트 추출
        for page_idx in range(min(2, len(doc))):
            page = doc[page_idx]
            extracted_text += page.get_text()

        doc.close()
        print("Extracted Text via fitz:", extracted_text)
    except Exception as e:
        print(f"Error during text extraction with fitz: {e}")
        return {
            "statusCode": 500,
            "body": f"Error during text extraction: {str(e)}"
        }

    # 4) OpenAI API를 사용한 텍스트 요약
    try:
        # 너무 긴 경우 일부 잘라냄 (예시: gpt-3.5-turbo를 사용)
        if len(extracted_text) > 4000:
            extracted_text = extracted_text[:4000]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text. "},
                {"role": "user", "content": f":Summarize the following text in Korean. The result should be one or two sentences that includes the most important part of the file.\n\n{extracted_text}"}
            ]
        )
        summary = response.choices[0].message.content
        print("Summary:", summary)
    except Exception as e:
        print(f"Error during summarization: {e}")
        return {
            "statusCode": 500,
            "body": f"Error during summarization: {str(e)}"
        }

    # 5) 결과 반환
    return {
        "statusCode": 200,
        "body": json.dumps({
            "summary": summary,
            "extracted_text": extracted_text
        })
    }
