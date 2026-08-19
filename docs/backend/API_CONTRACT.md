# AI Media Factory

# API Contract

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory backend provides REST API based on FastAPI.


Base URL:


http://localhost:8000


API version:


/api/v1/


Responsibilities:


- receive requests
- validate data
- call services
- return responses



API layer must not contain:

- business logic
- database queries
- AI logic



---

# 2. Response Format


Successful response example:


```json
{
  "status": "success",
  "data": {}
}

Error response:

{
  "status": "error",
  "message": "Description",
  "code": "ERROR_CODE"
}
3. Health API
GET /health

Purpose:

Check system availability.

Response:

{
  "status": "healthy"
}
4. Channel API
GET /api/v1/channels

Purpose:

Return all configured Telegram channels.

Response:

[
 {
  "id":1,
  "name":"AI News",
  "category":"technology",
  "status":"active"
 }
]
GET /api/v1/channels/{channel_id}

Purpose:

Return channel information.

Response:

{
"id":1,
"name":"AI News",
"category":"technology",
"language":"ru",
"status":"active"
}
POST /api/v1/channels/{channel_id}/run-research

Purpose:

Start Research Engine.

Request:

No body required.

Response:

{
 "status":"started",
 "topics_count":76
}

Workflow:

API

↓

Channel Service

↓

Research Service

↓

Research Engine

5. Content API
GET /api/v1/content/

Purpose:

Get stored content topics.

Query parameters:

channel_id

status

limit

offset

Example:

/api/v1/content/?channel_id=1&status=research

Response:

[
 {
  "id":42,
  "title":"New AI Model Released",
  "description":"New technology announcement",
  "score":8.5,
  "status":"research"
 }
]
6. Research Topic Object

Model:

ResearchTopic

Fields:

{
"id":42,
"channel_id":1,
"title":"Topic title",
"description":"Description",
"content":"Full text",
"score":8.5,
"sources":[
 "https://example.com"
],
"status":"research"
}
7. Writing Engine API (Future)
POST /api/v1/content/{topic_id}/generate

Purpose:

Create draft post from research topic.

Input:

ResearchTopic

Output:

DraftPost

Example:

{
"title":"AI breakthrough",
"body":"Telegram text",
"image_prompt":"future AI illustration",
"tags":[
"AI",
"Technology"
]
}
8. Publishing API (Future)
POST /api/v1/posts/{post_id}/publish

Purpose:

Publish approved post.

Process:

DraftPost

↓

Publishing Service

↓

Telegram Bot API

Response:

{
"status":"published",
"message_id":12345
}
9. Analytics API (Future)
GET /api/v1/analytics/{channel_id}

Purpose:

Return channel statistics.

Response:

{
"views":10000,
"engagement_rate":8.5
}
10. Validation Rules

Every endpoint must:

validate input using Pydantic
return documented schema
handle exceptions
log errors
11. HTTP Status Codes

200

Successful request.

201

Object created.

400

Invalid input.

404

Resource not found.

500

Internal server error.

12. API Development Rules

Before creating new endpoint:

Required:

Define purpose
Define request schema
Define response schema
Add service method
Add tests
Update documentation
13. Breaking Changes

Changing existing API requires:

update documentation
migration plan
compatibility check
End of API Contract

