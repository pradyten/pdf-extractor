# Repository Guidelines

## Project Structure & Module Organization
- `extractor.py` contains PDF rendering, template selection, and OpenAI calls.
- `templates/` holds JSON extraction templates referenced by `TEMPLATE_REGISTRY`.
- `src/streamlit_app.py` is the Hugging Face Space UI entrypoint.
- `Dockerfile` builds the Space image (Streamlit on port 8501).
- `.streamlit/config.toml` contains Space-friendly Streamlit server settings.
- `README.md` includes Space metadata front matter and usage notes.
- The UI relies on filename keywords to select templates (see `TEMPLATE_REGISTRY`).
- `sample/` contains demo documents used by the UI's sample picker.

## Build, Test, and Development Commands
- Install dependencies with `python -m pip install -r requirements.txt`.
- Local CLI extraction prompts for a PDF path and prints JSON:
  - `python extractor.py`
- Run the Space UI locally:
  - `streamlit run src/streamlit_app.py`
- Quick import sanity check:
  - `python -c "import extractor; print(extractor.DEFAULT_MODEL)"`

## Coding Style & Naming Conventions
- Keep 2-space indentation in `extractor.py`.
- Use snake_case for functions/variables, UPPER_SNAKE for constants, and add type hints for new functions.
- Template JSON filenames should be snake_case and registered via lowercase filename keywords in `TEMPLATE_REGISTRY`.

## Testing Guidelines
- No automated test suite exists yet. If adding tests, use `pytest` under `tests/`.
- Validate that model output matches the exact template schema and that filename keywords map to the right template.

## Commit & Pull Request Guidelines
- No established commit convention; use short, imperative subjects.
- PRs should include the document type, template files touched, example filename keyword, and any config/env changes.

## Security & Configuration Tips
- Set `OPENAI_API_KEY` for local runs and the Space; optionally override `EXTRACTOR_MODEL_ALIAS`.
- Avoid committing sensitive PDFs or output data; use redacted samples for demos.

## Automation
- `.github/workflows/sync-hf.yml` pushes `main` to the HF Space on each commit using `HF_TOKEN`.
- Treat GitHub as the source of truth; direct edits on HF may be overwritten.
