# Repository Guidelines

## Project Structure & Module Organization
- `extractor.py` contains the extraction pipeline: template selection, PDF-to-image rendering, and OpenAI ChatGPT inference calls.
- `templates/` holds JSON extraction templates referenced by `TEMPLATE_REGISTRY`. Filenames are snake_case and match document types (e.g., `templates/passport.json`).
- `README.md` is minimal; keep contributor guidance in this file.
- Add tests under `tests/` when a suite is introduced.

## Build, Test, and Development Commands
- Install dependencies with `python -m pip install -r requirements.txt`.
- There is no build step; this module is imported and called from other code. A quick import check:
  - `python -c "import extractor; print(extractor.DEFAULT_MODEL)"`
- Local CLI usage prompts for a PDF path and prints JSON:
  - `python extractor.py`
 - PDF rendering requires Pillow (installed via `requirements.txt`).

## Coding Style & Naming Conventions
- Follow the existing 2-space indentation in `extractor.py`.
- Use snake_case for functions/variables, UPPER_SNAKE for constants, and add type hints for new functions.
- Template JSON keys and filenames should stay consistent with the document type; register new templates in `TEMPLATE_REGISTRY` using lowercase filename keywords.

## Testing Guidelines
- No automated test suite exists yet. If adding tests, use `pytest` and place them under `tests/` (e.g., `tests/test_extractor.py`).
- Run tests with `python -m pytest` and validate JSON output matches the exact template schema.

## Commit & Pull Request Guidelines
- Git history only includes "Initial commit," so no convention is established. Use short, imperative subjects (e.g., "Add marriage certificate template").
- PRs should describe the document type, list template file names touched, include an example filename keyword, and call out any required env vars or API access changes.

## Security & Configuration Tips
- OpenAI access is required. Set `OPENAI_API_KEY`; optionally override `EXTRACTOR_MODEL_ALIAS`.
- Do not commit PDFs, credentials, or output containing sensitive data.
