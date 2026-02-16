# PDF-to-JSON Extractor with AI

Intelligent PDF document parser that extracts structured JSON data using OpenAI's GPT models and computer vision.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Author](#author)

## 🎯 Overview

This application converts PDF documents into structured JSON format using:
- **OpenAI GPT-4 Vision**: For intelligent content extraction
- **Template-based extraction**: Customizable JSON schemas for different document types
- **Streamlit UI**: Interactive web interface for easy PDF processing
- **Docker support**: Containerized deployment for production environments

Perfect for automating data extraction from resumes, invoices, forms, and other structured documents.

## ✨ Features

- **AI-Powered Extraction**: Uses GPT-4 Vision to understand document structure
- **Template System**: Pre-configured JSON templates for common document types
- **Batch Processing**: Handle multiple PDFs efficiently
- **Image Preview**: Visual confirmation of PDF pages before extraction
- **Format Validation**: Ensures extracted JSON matches defined schema
- **Hugging Face Spaces**: Ready for cloud deployment

## 🛠 Technology Stack

- **Python 3.9+** - Primary programming language
- **OpenAI API** - GPT-4 Vision for intelligent extraction
- **pypdfium2** - PDF rendering and image conversion
- **Streamlit** - Interactive web UI framework
- **Pillow (PIL)** - Image processing
- **Pandas** - Data manipulation

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup

1. Clone the repository:
\`\`\`bash
git clone https://github.com/pradyten/pdf-extractor.git
cd pdf-extractor
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Configure OpenAI API key:
\`\`\`bash
export OPENAI_API_KEY='your-api-key-here'
\`\`\`

## 💻 Usage

### Command Line
\`\`\`bash
python extractor.py path/to/document.pdf
\`\`\`

### Streamlit Web UI
\`\`\`bash
streamlit run src/streamlit_app.py
\`\`\`

### Docker
\`\`\`bash
docker build -t pdf-extractor .
docker run -p 8501:8501 -e OPENAI_API_KEY='your-key' pdf-extractor
\`\`\`

## ⚙️ Configuration

Define custom templates in \`extractor.py\` for different document types (resumes, invoices, forms).

## 🎓 Use Cases

- **HR & Recruitment**: Batch process resume PDFs
- **Accounting**: Extract invoice data
- **Data Entry**: Automate form digitization
- **Document Management**: Convert scanned documents to searchable JSON

## 🔒 Security & Privacy

- Never commit API keys - use environment variables
- PDFs are processed in-memory, not stored
- Review OpenAI's data usage policies for compliance

## 👨‍💻 Author

**Pradyumn Tendulkar**

Data Science Graduate Student | ML Engineer

- GitHub: [@pradyten](https://github.com/pradyten)
- LinkedIn: [Pradyumn Tendulkar](https://www.linkedin.com/in/p-tendulkar/)
- Email: pktendulkar@wpi.edu

---

⭐ If you found this project helpful, please consider giving it a star!

📝 **License:** MIT
