import hashlib
import json
import os
import sys

import streamlit as st
import pypdfium2 as pdfium

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
  sys.path.insert(0, ROOT_DIR)

from extractor import extract_using_openai_from_pdf_bytes


st.set_page_config(page_title="PDF Extractor", layout="wide")

st.markdown(
  """
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');
  :root {
    --bg-0: #f3ede4;
    --bg-1: #fbf5ea;
    --panel: #ffffff;
    --border: rgba(16, 24, 40, 0.12);
    --text: #121212;
    --muted: #5b616b;
    --accent: #d4552d;
    --accent-dark: #b44725;
    --shadow: 0 18px 50px rgba(20, 20, 20, 0.12);
  }
  html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px 600px at 10% -10%, var(--bg-0) 0%, #f7f2e9 45%, var(--bg-1) 100%);
    color: var(--text);
    font-family: "Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  h1, h2, h3, h4, h5 {
    font-family: "Space Grotesk", system-ui, -apple-system, "Segoe UI", sans-serif;
    letter-spacing: -0.02em;
  }
  .main .block-container {
    max-width: 1200px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
  }
  div[data-testid="column"] > div {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.25rem 1.5rem 1.5rem 1.5rem;
    box-shadow: var(--shadow);
  }
  .stButton > button {
    background: var(--accent);
    color: #ffffff;
    border: none;
    border-radius: 999px;
    padding: 0.65rem 1.4rem;
    font-weight: 600;
  }
  .stButton > button:hover {
    background: var(--accent-dark);
    color: #ffffff;
  }
  div[data-testid="stFileUploader"] {
    border: 1px dashed rgba(16, 24, 40, 0.18);
    border-radius: 14px;
    padding: 0.6rem;
    background: rgba(248, 244, 236, 0.6);
  }
  .stAlert {
    border-radius: 12px;
  }
  pre, code, .stCodeBlock {
    border-radius: 12px !important;
  }
  #MainMenu, footer {
    visibility: hidden;
  }
  </style>
  """,
  unsafe_allow_html=True,
)


def _render_pdf_preview(pdf_bytes: bytes) -> None:
  pdf = None
  try:
    pdf = pdfium.PdfDocument(pdf_bytes)
    if len(pdf) < 1:
      st.info("No pages found in this PDF.")
      return
    page = pdf[0]
    pil_image = page.render(scale=2.0).to_pil()
    st.image(pil_image, caption="Preview (page 1)", use_column_width=True)
  except Exception as exc:  # pragma: no cover - UI preview path
    st.warning(f"Preview unavailable: {exc}")
  finally:
    if pdf is not None:
      pdf.close()


def _load_pdf_state(uploaded_file) -> tuple[bytes, str, str]:
  pdf_bytes = uploaded_file.getvalue()
  digest = hashlib.sha256(pdf_bytes).hexdigest()
  return pdf_bytes, uploaded_file.name, digest


def _build_download_name(filename: str) -> str:
  base = os.path.splitext(filename)[0] if filename else "extraction"
  safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in base)
  if not safe:
    safe = "extraction"
  return f"{safe}_extracted.json"


if "extract_result" not in st.session_state:
  st.session_state.extract_result = None
if "extract_error" not in st.session_state:
  st.session_state.extract_error = None
if "extract_digest" not in st.session_state:
  st.session_state.extract_digest = None
if "extract_filename" not in st.session_state:
  st.session_state.extract_filename = None
if "pdf_bytes" not in st.session_state:
  st.session_state.pdf_bytes = None
if "pdf_filename" not in st.session_state:
  st.session_state.pdf_filename = None
if "pdf_digest" not in st.session_state:
  st.session_state.pdf_digest = None


st.markdown("## PDF Extractor")
st.markdown(
  "Upload a PDF on the left, preview it, then click Extract to generate "
  "structured JSON on the right."
)

left, right = st.columns([1, 1], gap="large")

with left:
  st.markdown("### Upload + Preview")
  uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"],
    accept_multiple_files=False,
    label_visibility="collapsed",
    key="pdf_uploader",
    help="File name should include a known keyword (for example: resume, passport, i129).",
  )
  clear_clicked = st.button(
    "Clear upload",
    disabled=uploaded_file is None and st.session_state.pdf_bytes is None,
  )
  if clear_clicked:
    st.session_state.pdf_bytes = None
    st.session_state.pdf_filename = None
    st.session_state.pdf_digest = None
    st.session_state.extract_result = None
    st.session_state.extract_error = None
    st.session_state.extract_digest = None
    st.session_state.extract_filename = None
    st.session_state.pdf_uploader = None
    st.rerun()

  if uploaded_file is None:
    st.info("Upload a PDF to preview it here.")
  else:
    pdf_bytes, filename, digest = _load_pdf_state(uploaded_file)
    if st.session_state.pdf_digest != digest:
      st.session_state.pdf_bytes = pdf_bytes
      st.session_state.pdf_filename = filename
      st.session_state.pdf_digest = digest
      st.session_state.extract_result = None
      st.session_state.extract_error = None
      st.session_state.extract_digest = digest
      st.session_state.extract_filename = filename

    st.markdown(f"**File:** `{st.session_state.pdf_filename}`")
    _render_pdf_preview(st.session_state.pdf_bytes)

  st.markdown("#### Notes")
  st.caption(
    "Template selection is inferred from the filename. If extraction fails, "
    "rename the file to include a supported keyword (for example: "
    "`resume.pdf`, `passport_jane.pdf`, `i129_petition.pdf`)."
  )

with right:
  st.markdown("### Extract")
  model_choice = st.selectbox(
    "Model",
    ["default", "gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-4o"],
    index=1,
    help="Choose a model or use default (EXTRACTOR_MODEL_ALIAS).",
  )

  has_api_key = bool(os.getenv("OPENAI_API_KEY"))
  if not has_api_key:
    st.warning("OPENAI_API_KEY is not set. Add it to your environment or Space secrets.")

  extract_clicked = st.button(
    "Extract",
    use_container_width=False,
    disabled=st.session_state.pdf_bytes is None or not has_api_key,
  )

  if extract_clicked:
    with st.spinner("Extracting structured JSON..."):
      try:
        result = extract_using_openai_from_pdf_bytes(
          st.session_state.pdf_bytes,
          st.session_state.pdf_filename,
          model=model_choice,
        )
        st.session_state.extract_result = result
        st.session_state.extract_error = None
      except Exception as exc:  # pragma: no cover - runtime error path
        message = str(exc)
        if "403" in message or "PermissionDenied" in message:
          message = (
            "OpenAI request was rejected (403). "
            "Check OPENAI_API_KEY, model access, and billing."
          )
        st.session_state.extract_error = message
        st.session_state.extract_result = None

  if st.session_state.extract_error:
    st.error(st.session_state.extract_error)

  if st.session_state.extract_result is None:
    st.info("Extraction output will appear here.")
  else:
    st.markdown("#### JSON Output")
    json_text = json.dumps(
      st.session_state.extract_result,
      indent=2,
      ensure_ascii=False,
    )
    st.code(json_text, language="json")
    st.download_button(
      "Download JSON",
      data=json_text,
      file_name=_build_download_name(st.session_state.pdf_filename or ""),
      mime="application/json",
    )
