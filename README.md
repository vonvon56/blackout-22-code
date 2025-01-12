# blackout-22-code
2025 Blackout Hackathon

# Slack Accessibility Suite

**BLACKOUT 2025** (01.11-01.12) 출품작
- 서울대, 연세대, 고려대, KAIST, POSTECH, GIST 연합 해커톤 
- 🖧 AWS & Slack 트랙

Slack Accessibility Suite는 시각장애 학생들이 교육 환경에서 Slack을 보다 쉽게 사용할 수 있도록 돕는 프로젝트입니다. AWS 및 기타 최신 기술을 활용하여 Slack 채널에서의 접근성을 개선하고, 이미지 설명, 문서 요약, 맞춤법 검사 및 공지사항 요약 기능을 제공합니다.

## Lambda API
| 기능 | url | 입력 형식 | 반환 형식 | 메서드 |
| --- | --- | --- | --- | --- |
| pdf 요약문 생성| [https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf](https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf-upload) |{    "type": "file_shared", "file_id": "F088BK4FNN8","user_id": "U086YN29A2G","file": { "id": "F088BK4FNN8"},"channel_id": "C088LRXLMRP","event_ts": "1736625132.003300" } | {"summary": "어쩌고", "extracted_text": “원래 본문 내용이 저쩌고"} | POST |
| 이미지 대체텍스트 생성 | [https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/](https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf-upload)jpg | {"url_private": "https://files.slack.com/files-pri/T07UKV72WTC-F08850RE2MT/image.png" } | {"alt_text": "이 사진이 어쩌고저쩌고"} | POST |
| 맞춤법&오타 자동 수정 | https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/typocorrect | {"text": "이렇게 쓰면 안되요?"} | {"corrected_message": "이렇게 쓰면 안 돼요?"} |POST |