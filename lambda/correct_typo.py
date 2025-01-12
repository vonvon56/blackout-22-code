import json
import os
import requests
import openai  # GPT API 호출을 위한 라이브러리

def lambda_handler(event, context):
    print("Lambda function invoked!")
    print(f"Event Data: {json.dumps(event)}")
    try:
        # 'body' 키가 없으면 event 자체에서 text를 검색
        if "body" in event:
            body = json.loads(event["body"])
            user_message = body.get("text", "")
        else:
            user_message = event.get("text", "")  # event에 직접 text가 포함된 경우 처리

        if not user_message:
            raise ValueError("Missing 'text' in the request body.")

        # GPT API를 통해 메시지 교정
        corrected_message = correct_message(user_message)

        return {
            "statusCode": 200,
            "body": json.dumps({"corrected_message": corrected_message})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def correct_message(message):
    try:
        print(f"Correcting message: {message}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that corrects sentences."},
                {"role": "user", "content": f"""The following is a sentence written by a visually impaired person, and may contain voice recognition errors or typos. Correct the spelling and typos in this sentence to make it look natural. 
1. Keep the meaning of the sentence as is and correct it by only looking for typos or misspellings.
2. Do not modify punctuation marks arbitrarily.
3. Use same language as the input language\n\n{message}"""}
            ]
        )
        corrected_text = response.choices[0].message.content.strip()
        print(f"Corrected Message: {corrected_text}")
        return corrected_text
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error in message correction"
