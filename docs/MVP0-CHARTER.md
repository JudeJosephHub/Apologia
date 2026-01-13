# Apologia — MVP0 Charter

## Goal
Upload a sermon PPTX, review slide-by-slide proofreading suggestions, apply accepted changes, and download an updated PPTX.

## MVP0 Features
- Upload PPTX with basic metadata (week/date, series, sermon name, pastor)
- Extract slide text (title/body/notes)
- Generate slide-by-slide proofreading suggestions
- Review UI: Accept / Reject / Edit per slide
- Generate updated PPTX (text-only replacement; preserve layout)
- Download updated PPTX
- Store sermon + slide decisions + outputs

## Out of Scope (MVP0)
- Auto-replacing Bible verse text (only highlight questionable references)
- Book builder / chapter compilation
- Multi-user roles and permissions
- Audio transcription

## Guardrails
- No change is applied without user approval
- Never alter doctrine or intended meaning
- Always show original vs suggested vs final text

## Success Criteria
A pastor can upload a real sermon PPTX and download a corrected PPTX with the same layout.
