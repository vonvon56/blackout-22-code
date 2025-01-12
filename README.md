# 🔓 Slack Accessibility Suite 🔓

🌃 **BLACKOUT 2025** 🌃 (01.11-01.12) 출품작
- 👩‍💻 서울대, 연세대, 고려대, KAIST, POSTECH, GIST 연합 해커톤 
- 🖧   AWS & Slack 트랙
- 🔍 주제: AWS와 Slack을 활용하여 **AI Driven Campus**를 달성하기 위한 솔루션을 만들어라

Slack Accessibility Suite는 **시각장애 학생**들이 **교육 환경에서 Slack을 보다 쉽게** 사용할 수 있도록 돕는 프로젝트입니다. 

AWS lambda와 openai api, [alt text](https://alttext.ai/account/api_keys)를 활용하여 **Slack 채널에서의 접근성을 개선**하고, **이미지의 대체 텍스트 생성, 문서 요약, 맞춤법 검사** 기능을 제공합니다.

## 👥 Members

(소개 추가 예정)

양식: 이름, github 아이디, 역할, 한줄소개

## λ Lambda API
| 기능 | url | 입력 형식 | 반환 형식 | 메서드 |
| --- | --- | --- | --- | --- |
| pdf 요약문 생성| [https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf](https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf-upload) |{    "type": "file_shared", "file_id": "F088BK4FNN8","user_id": "U086YN29A2G","file": { "id": "F088BK4FNN8"},"channel_id": "C088LRXLMRP","event_ts": "1736625132.003300" } | {"summary": "어쩌고", "extracted_text": “원래 본문 내용이 저쩌고"} | POST |
| 이미지 대체텍스트 생성 | [https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/](https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf-upload)jpg | {"url_private": "https://files.slack.com/files-pri/T07UKV72WTC-F08850RE2MT/image.png" } | {"alt_text": "이 사진이 어쩌고저쩌고"} | POST |
| 맞춤법&오타 자동 수정 | https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/typocorrect | {"text": "이렇게 쓰면 안되요?"} | {"corrected_message": "이렇게 쓰면 안 돼요?"} |POST |

## 🚀 주요 기능

### 1. 이미지 대체 텍스트 생성

- Slack에 업로드된 이미지를 감지하여 lambda api에 전송한다.

- [alttext.ai API](https://alttext.ai/account/api_keys)를 사용하여 대체 텍스트를 생성한다.


### 2. PDF 요약 메시지 전송

- PyMuPDF(fitz) 라이브러리를 활용하여 Slack에 업로드된 PDF 파일의 텍스트를 읽어온다.

- OpenAI GPT API를 통해 텍스트 요약문을 생성한다.


### 3. 맞춤법 검사

- Slack 메시지 전송 시 openai api를 통해 맞춤법과 오타를 교정한다.

- 교정된 메시지는 메시지 Slack 채널에 자동으로 전송한다.

## ⚙️ 기술 스택 ⚙️
🤖 멀티모달이 아니라는 openai api의 한계 극복을 위한 **[alttext.ai API](https://alttext.ai/account/api_keys)** 사용 
-> 이미지를 직접 input으로 받을 수 있음

💻 AI driven campus 환경 자동화를 위한 **Slack app** 구축

🛠️ 서버리스 환경 구축을 위한 **AWS lambda** 서비스 활용

## ℹ️ 사용 예시

[맞춤법_시연](https://github.com/user-attachments/assets/a309ce45-efe1-429c-b20f-232f3a89c34e)

- 맞춤법이 틀린 경우 해당 채팅 자동 수정
- 틀리지 않은 경우 반응하지 않음