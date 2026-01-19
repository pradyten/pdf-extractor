import base64
import hashlib
import json
import os
import sys

import streamlit as st
import streamlit.components.v1 as components

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
  encoded = base64.b64encode(pdf_bytes).decode("utf-8")
  pdf_html = f"""
  <iframe
    src="data:application/pdf;base64,{encoded}"
    width="100%"
    height="540"
    style="border: none; border-radius: 14px;"
  ></iframe>
  """
  components.html(pdf_html, height=560)


def _load_pdf_state(uploaded_file) -> tuple[bytes, str, str]:
  pdf_bytes = uploaded_file.getvalue()
  digest = hashlib.sha256(pdf_bytes).hexdigest()
  return pdf_bytes, uploaded_file.name, digest


if "extract_result" not in st.session_state:
  st.session_state.extract_result = None
if "extract_error" not in st.session_state:
  st.session_state.extract_error = None
if "extract_digest" not in st.session_state:
  st.session_state.extract_digest = None
if "extract_filename" not in st.session_state:
  st.session_state.extract_filename = None


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
    label_visibility="collapsed",
    help="File name should include a known keyword (for example: resume, passport, i129).",
  )

  if uploaded_file is None:
    st.info("Upload a PDF to preview it here.")
  else:
    pdf_bytes, filename, digest = _load_pdf_state(uploaded_file)
    if st.session_state.extract_digest != digest:
      st.session_state.extract_result = None
      st.session_state.extract_error = None
      st.session_state.extract_digest = digest
      st.session_state.extract_filename = filename

    st.markdown(f"**File:** `{filename}`")
    _render_pdf_preview(pdf_bytes)

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

  if not os.getenv("OPENAI_API_KEY"):
    st.warning("OPENAI_API_KEY is not set. Add it to your environment or Space secrets.")

  extract_clicked = st.button("Extract", use_container_width=False)

  if extract_clicked:
    if uploaded_file is None:
      st.session_state.extract_error = "Please upload a PDF first."
    else:
      with st.spinner("Extracting structured JSON..."):
        try:
          result = extract_using_openai_from_pdf_bytes(
            pdf_bytes,
            filename,
            model=model_choice,
          )
          st.session_state.extract_result = result
          st.session_state.extract_error = None
        except Exception as exc:  # pragma: no cover - runtime error path
          st.session_state.extract_error = str(exc)
          st.session_state.extract_result = None

  if st.session_state.extract_error:
    st.error(st.session_state.extract_error)

  if st.session_state.extract_result is None:
    st.info("Extraction output will appear here.")
  else:
    st.markdown("#### JSON Output")
    st.code(
      json.dumps(st.session_state.extract_result, indent=2, ensure_ascii=False),
      language="json",
    )
