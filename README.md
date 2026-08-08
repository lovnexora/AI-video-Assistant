# 🎬 AI Video assistant

An intelligent, end-to-end Python application built with **Streamlit**, **OpenAI Whisper**, and **LangChain**. It automatically downloads audio from YouTube URLs or local media files, transcribes speech to text locally, chunks the audio for performance, and builds a vector storage engine to allow interactive Q&A over video content.

---

## ✨ Features

- 📹 **Multi-Source Support**: Accepts direct YouTube links or local audio/video file uploads.
- ⚡ **Local Speech-to-Text**: Powered by OpenAI's Whisper model (CPU-optimized with zero external API transcription costs).
- 🧩 **Smart Audio Chunking**: Automatically slices heavy audio into manageable segments for fast, reliable processing.
- 💬 **Interactive RAG / Q&A**: Uses **LangChain** and vector embeddings so you can chat directly with your video content.
- 🛡️ **Cross-Platform Auto-Setup**: Integrates `static-ffmpeg` to configure local binary dependencies automatically across Linux and Windows environments.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Transcription**: OpenAI Whisper
- **LLM & RAG Orchestration**: LangChain + Mistral AI API
- **Audio Processing**: PyDub + yt-dlp + static-ffmpeg

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed. We recommend using `uv` for fast package management.

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME

# Install dependencies using uv
uv pip install -r requirements.txt
