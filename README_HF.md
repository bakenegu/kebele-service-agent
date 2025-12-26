---
title: Kebele Service Agent
emoji: 🇪🇹
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.26.0
app_file: app.py
pinned: false
license: mit
---

# 🇪🇹 Kebele Service Agent MVP

AI-powered conversational agent for Ethiopian Kebele services. This MVP supports:

- **Birth Certificate Registration** with document upload and PDF generation
- **Digital ID Appointment Booking**
- **Natural Language Processing** - Users can type in Amharic or English
- **Multi-field Extraction** - Extract multiple fields from a single message
- **Auto-advance** - Automatically progresses through workflow when fields are complete

## Features

✨ **Conversational AI**: Natural language input instead of strict form fields  
📄 **PDF Generation**: Automatic birth certificate PDF creation  
📎 **Document Upload**: Support for 1-3 files (images/PDF)  
🌍 **Bilingual**: Supports Amharic (አማርኛ) and English  
🔄 **State Machine**: Deterministic workflow ensures data integrity

## Setup

### For Hugging Face Spaces:

1. **Add OpenAI API Key as Secret**:
   - Go to your Space settings
   - Navigate to "Variables and secrets"
   - Add a new secret: `OPENAI_API_KEY` with your OpenAI API key

2. **Optional Environment Variables**:
   - `OPENAI_MODEL`: Model to use (default: "gpt-4-turbo")
   - `GRADIO_SHARE`: Set to "True" to create public link (default: "False")

The app will automatically use the API key from secrets.

### For Local Development:

1. Install dependencies:
```bash
uv sync
# or
pip install -r requirements.txt
```

2. Create `.env` file:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo
```

3. Run:
```bash
uv run python -m src.main
# or
python app.py
```

## Usage

1. **Start a conversation**: Choose service (A for Birth Certificate, B for ID Appointment)
2. **Provide information**: Type naturally, e.g., "My child is Tadesse Taffa born 12/10/2020, boy"
3. **Upload documents**: When prompted, upload 1-3 files
4. **Complete workflow**: Follow prompts to complete registration
5. **Download PDF**: Get your generated birth certificate PDF

## Technology Stack

- **Gradio**: Web UI framework
- **LangChain**: LLM integration
- **OpenAI**: GPT models for NLU
- **ReportLab**: PDF generation
- **Pydantic**: Structured output validation

## License

MIT

