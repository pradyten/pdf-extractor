import os
import json
import base64
import io
from typing import Dict, Any, List, Tuple, Optional

from openai import OpenAI
import pypdfium2 as pdfium


# path to templates folder (relative to this file)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


TEMPLATE_REGISTRY: Dict[str, Dict[str, str]] = {
  # keyword in PDF filename (lowercase) : { document_type, template_file }

  # Immigration forms
  "i129": {
    "document_type": "USCIS Form I-129 H-1B Petition",
    "template_file": "i129_h1b_petition.json",
  },
  "i94": {
    "document_type": "Form I-94 Arrival/Departure Record",
    "template_file": "i_94.json",
  },
  "i-94": {
    "document_type": "Form I-94 Arrival/Departure Record",
    "template_file": "i_94.json",
  },
  "i20": {
    "document_type": "Form I-20 Certificate of Eligibility",
    "template_file": "proof_of_in_country_status.json",
  },
  "i-20": {
    "document_type": "Form I-20 Certificate of Eligibility",
    "template_file": "proof_of_in_country_status.json",
  },

  # Identity documents
  "passport": {
    "document_type": "Passport",
    "template_file": "passport.json",
  },
  "visa": {
    "document_type": "US Visa",
    "template_file": "us_visa.json",
  },

  # Education documents
  "transcript": {
    "document_type": "Academic Transcript",
    "template_file": "school_transcripts.json",
  },
  "diploma": {
    "document_type": "Diploma",
    "template_file": "diplomas.json",
  },

  # Employment documents
  "employment letter": {
    "document_type": "Employment Letter",
    "template_file": "employment_letter.json",
  },
  "offer letter": {
    "document_type": "Employment Letter",
    "template_file": "employment_letter.json",
  },
  "offer-letter": {
    "document_type": "Employment Letter",
    "template_file": "employment_letter.json",
  },
  "offer_letter": {
    "document_type": "Employment Letter",
    "template_file": "employment_letter.json",
  },
  "employment_letter": {
    "document_type": "Employment Letter",
    "template_file": "employment_letter.json",
  },
  "employment": {
    "document_type": "Employment Letter",
    "template_file": "employment_letter.json",
  },
  "resume": {
    "document_type": "Resume/CV",
    "template_file": "resume.json",
  },
  "cv": {
    "document_type": "Resume/CV",
    "template_file": "resume.json",
  },

  # Tax and corporate documents
  "fein": {
    "document_type": "Corporate Tax Returns",
    "template_file": "corporate_tax_returns.json",
  },
  "cp575": {
    "document_type": "Corporate Tax Returns",
    "template_file": "corporate_tax_returns.json",
  },
  "tax": {
    "document_type": "Corporate Tax Returns",
    "template_file": "corporate_tax_returns.json",
  },

  # Personal documents
  "marriage": {
    "document_type": "Marriage Certificate",
    "template_file": "marriage_certificate.json",
  },
  "marriage_certificate": {
    "document_type": "Marriage Certificate",
    "template_file": "marriage_certificate.json",
  },

  # Proof of status
  "proof": {
    "document_type": "Proof of In-Country Status",
    "template_file": "proof_of_in_country_status.json",
  },
}


# Logical model aliases for this extractor (OpenAI ChatGPT models).
ALLOWED_MODELS = [
  "default",
  "gpt-4.1-mini",
  "gpt-4.1",
  "gpt-4o-mini",
  "gpt-4o",
  # Legacy/dated aliases kept for compatibility.
  "gpt-4.1-2025-04-14",
  "gpt-4.1-mini-2025-04-14",
  "gpt-5-2025-08-07",
  "gpt-5-mini-2025-08-07",
]

DEFAULT_MODEL = os.getenv("EXTRACTOR_MODEL_ALIAS", "gpt-4.1-mini")

OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
_openai_client: Optional[OpenAI] = None


def load_template(template_file: str) -> Dict[str, Any]:
  path = os.path.join(TEMPLATES_DIR, template_file)
  if not os.path.exists(path):
    raise FileNotFoundError(f"Template not found: {path}")
  with open(path, "r", encoding="utf-8") as fh:
    return json.load(fh)


def infer_template_from_filename(filename: str) -> Tuple[str, Dict[str, Any]]:
  """
  Look at the PDF file name and decide which document_type + template to use.

  Example:
    - 'I129 HALF.pdf'      -> matches 'i129' -> uses i129_h1b_petition.json
    - 'passport_rohan.pdf' -> matches 'passport' -> uses passport.json
    - 'F1_visa_page1.pdf'  -> matches 'visa' -> uses us_visa.json
    - 'i94_record.pdf'     -> matches 'i94' -> uses i_94.json
  """
  basename = os.path.basename(filename).lower()

  for keyword, cfg in TEMPLATE_REGISTRY.items():
    if keyword in basename:
      document_type = cfg["document_type"]
      template = load_template(cfg["template_file"])
      return document_type, template

  # fallback: raise to force user to add mapping or rename file
  raise ValueError(
    f"Could not infer document type from filename '{basename}'. "
    f"Known keywords: {list(TEMPLATE_REGISTRY.keys())}"
  )


def pdf_bytes_to_base64_images(pdf_bytes: bytes, max_pages: int = 10) -> List[str]:
  """
  Render each page of the PDF bytes to a JPEG image and return a list of
  base64-encoded image strings (no data URL prefix). Limit pages by max_pages.
  """
  pdf = pdfium.PdfDocument(pdf_bytes)
  images: List[str] = []

  try:
    total_pages = len(pdf)
    if max_pages is not None and max_pages > 0:
      page_count = min(total_pages, max_pages)
    else:
      page_count = total_pages

    # Adaptive scale/quality to keep payloads manageable.
    if page_count <= 2:
      scale = 4.17   # ~300 DPI
      quality = 80
    elif page_count <= 10:
      scale = 2.0    # ~145 DPI
      quality = 60
    else:
      scale = 1.5    # ~110 DPI
      quality = 60

    for page_index in range(page_count):
      page = pdf[page_index]
      pil_image = page.render(scale=scale).to_pil()

      buffered = io.BytesIO()
      pil_image.save(buffered, format="JPEG", quality=quality)
      img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
      images.append(img_b64)

      buffered.close()
      pil_image.close()
  finally:
    pdf.close()

  return images


def build_extraction_prompt(document_type: str, template: Dict[str, Any]) -> str:
  """
  Build a prompt that instructs the model to extract data into the
  exact JSON structure defined by the template.
  """
  return f"""
You are a document data extraction system.

Document Type: {document_type}

Extract all information from the provided document image(s) and return it in the following exact JSON structure:

{json.dumps(template, indent=2)}

Instructions:
- Output only valid JSON matching exactly the structure above
- Do NOT add explanations
- Do NOT wrap the JSON in markdown, backticks, or code fences
- If a field is missing, set it to ""
- Use the exact field names; do not modify the structure
- Extract information from ALL pages
"""


def _get_openai_client() -> OpenAI:
  global _openai_client
  if _openai_client is None:
    api_key = os.getenv(OPENAI_API_KEY_ENV)
    if not api_key:
      raise RuntimeError(
        f"{OPENAI_API_KEY_ENV} is not set. "
        "Set it in your environment or CI secrets."
      )
    _openai_client = OpenAI(api_key=api_key)
  return _openai_client


def _extract_text_from_response(response: Any) -> str:
  output_text = getattr(response, "output_text", None)
  if isinstance(output_text, str) and output_text.strip():
    return output_text.strip()

  output = getattr(response, "output", None)
  if isinstance(output, list):
    parts: List[str] = []
    for item in output:
      content = getattr(item, "content", None)
      if content is None and isinstance(item, dict):
        content = item.get("content")
      if isinstance(content, list):
        for block in content:
          if isinstance(block, dict):
            block_type = block.get("type")
            if block_type in ("output_text", "text"):
              parts.append(block.get("text", ""))
          else:
            block_type = getattr(block, "type", None)
            if block_type in ("output_text", "text"):
              parts.append(getattr(block, "text", ""))
    return "".join(parts).strip()

  return ""


def _invoke_openai(prompt: str, images: List[str], model: str) -> Any:
  """
  Call OpenAI ChatGPT with the given prompt + images and return the response.
  """
  client = _get_openai_client()

  user_content: List[Dict[str, Any]] = [
    {"type": "input_text", "text": prompt},
  ]

  for img_b64 in images:
    user_content.append(
      {
        "type": "input_image",
        "image_url": f"data:image/jpeg;base64,{img_b64}",
      }
    )

  return client.responses.create(
    model=model,
    temperature=0,
    input=[
      {
        "role": "system",
        "content": [
          {
            "type": "input_text",
            "text": "You are a precise document extraction engine.",
          }
        ],
      },
      {
        "role": "user",
        "content": user_content,
      },
    ],
  )


def call_openai_extract(
  document_type: str,
  template: Dict[str, Any],
  images: List[str],
  model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
  """
  Call OpenAI ChatGPT to extract structured JSON for the given
  document type and template.
  """
  resolved_model = DEFAULT_MODEL if model == "default" else model

  if resolved_model not in ALLOWED_MODELS:
    raise ValueError(
      f"Unsupported model alias '{model}'. "
      f"Supported values: {ALLOWED_MODELS}. "
      "This extractor uses OpenAI ChatGPT models."
    )

  prompt = build_extraction_prompt(document_type, template)

  response = _invoke_openai(prompt, images, resolved_model)
  json_str = _extract_text_from_response(response).strip()

  # Strip optional markdown fences (```json ... ```)
  if json_str.startswith("```"):
    lines = json_str.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
      lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
      lines = lines[:-1]
    json_str = "\n".join(lines).strip()

  if not json_str:
    raise ValueError(
      "Model response did not contain any text content to parse as JSON."
    )

  try:
    return json.loads(json_str)
  except json.JSONDecodeError as exc:
    snippet = json_str[:500]
    raise ValueError(
      f"Model output was not valid JSON: {exc}. "
      f"First 500 characters of response: {snippet!r}"
    ) from exc


def extract_using_openai_from_pdf_bytes(
  pdf_bytes: bytes,
  filename: str,
  max_pages: int = 10,
  model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
  """
  Backwards-compatible entrypoint used by the Vision Lambda.

  Despite the legacy name, this now uses OpenAI ChatGPT to perform the
  extraction while preserving the JSON contract.
  """
  document_type, template = infer_template_from_filename(filename)
  images = pdf_bytes_to_base64_images(pdf_bytes, max_pages=max_pages)
  if not images:
    raise RuntimeError("No images were extracted from PDF")

  return call_openai_extract(document_type, template, images, model=model)


def _prompt_for_pdf_path() -> str:
  """
  Simple CLI helper for local runs. Web UI integrations can call
  extract_using_openai_from_pdf_bytes directly instead.
  """
  path = input("Enter path to PDF: ").strip()
  if not path:
    raise SystemExit("No PDF path provided.")
  return path


if __name__ == "__main__":
  pdf_path = _prompt_for_pdf_path()
  with open(pdf_path, "rb") as fh:
    pdf_data = fh.read()
  result = extract_using_openai_from_pdf_bytes(pdf_data, pdf_path)
  print(json.dumps(result, ensure_ascii=False))
