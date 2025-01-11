# blackout-22-code
2025 Blackout Hackathon

## Lambda API
| url | 입력 형식 | 반환 형식 | 메서드 |
| --- | --- | --- | --- |
| [https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf](https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf-upload) | {"bucket_name": "blackout-22-pdfstorage", "file_name": "An evolutionary account of loanword-induced sound change in Japanes.pdf"} | {"summary": "어쩌고", "extracted_text": “원래 본문 내용이 저쩌고"} | POST |
| [https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/](https://zpueuoghm7.execute-api.us-east-1.amazonaws.com/blackout-22-deploy/pdf-upload)jpg | { "event": { "type": "message", "files": [ { "id": "F1234567890", "name": "example.jpg", "filetype": "jpg", "url_private": "https://files.slack.com/files-pri/T07UKV72WTC-F08828PMUSJ/likelion.png" } ] } } | {"alt_text": "이 사진이 어쩌고저쩌고"} | POST |