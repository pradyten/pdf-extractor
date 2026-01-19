---
title: Pdf Extractor
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: pdf_extractor
---

# Pdf Extractor

This repository contains a PDF-to-JSON extractor and (optionally) a Hugging Face
Space UI.

## What's here
- `extractor.py` converts PDFs to images, selects a JSON template, and calls
  OpenAI to extract structured data.
- `templates/` holds JSON schemas used for extraction.
- `src/streamlit_app.py` is the Space UI entrypoint (when present).

## Quick start (local)
1. `python -m pip install -r requirements.txt`
2. `python extractor.py`
3. Provide a PDF filename that matches a keyword in `TEMPLATE_REGISTRY`
   (example: `resume.pdf`).

## Hugging Face Space
This Space is configured to run a Streamlit app on port 8501. Set
`OPENAI_API_KEY` in Space secrets to enable extraction.
