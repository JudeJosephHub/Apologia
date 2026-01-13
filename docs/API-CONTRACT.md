# API Contract (MVP0)

## POST /api/sermons
Upload a sermon PPTX + metadata.

Request: multipart/form-data
- file: pptx
- weekOrDate: string
- seriesName: string
- sermonName: string
- pastorName: string

Response:
{
  "sermonId": "string",
  "status": "uploaded"
}

## GET /api/sermons
List sermons.

Response:
[
  {
    "sermonId": "string",
    "weekOrDate": "string",
    "seriesName": "string",
    "sermonName": "string",
    "pastorName": "string",
    "status": "uploaded|processing|reviewing|ready|failed"
  }
]

## GET /api/sermons/{sermonId}/slides
Return slide-by-slide content for review.

Response:
[
  {
    "slideId": "string",
    "slideNumber": 1,
    "originalText": "string",
    "suggestedText": "string",
    "finalText": "string|null",
    "decision": "pending|accepted|rejected|edited",
    "issues": [
      { "type": "spelling|grammar|verse_ref", "message": "string", "severity": "low|med|high" }
    ]
  }
]

## POST /api/sermons/{sermonId}/slides/{slideId}/decision
Save decision per slide.

Request:
{
  "decision": "accepted|rejected|edited",
  "finalText": "string"
}

Response:
{ "ok": true }

## POST /api/sermons/{sermonId}/generate-updated-pptx
Generate updated PPTX from final decisions.

Response:
{ "status": "ready" }

## GET /api/sermons/{sermonId}/download-updated-pptx
Downloads the updated PPTX.
