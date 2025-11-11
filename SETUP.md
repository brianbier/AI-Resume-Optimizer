# 🚀 Local Setup Guide

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd resume-optimization-crew
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - Enter your API keys in the sidebar
   - Upload your resume and analyze!

## API Keys Needed

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Serper API Key**: Get from [Serper.dev](https://serper.dev/)

## Important Notes

- **Fresh session required**: For different resumes, restart the app (`Ctrl+C` then run again)
- **Local only**: This app is designed for local use due to ChromaDB memory limitations
- **Your data stays local**: All analysis happens on your machine

## Troubleshooting

If you get ChromaDB errors:
1. Stop the app (`Ctrl+C`)
2. Delete any `.chroma` folders: `rm -rf .chroma`
3. Restart: `streamlit run streamlit_app.py`