import os
from groq import Groq

# Initialize Groq client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    return Groq(api_key=api_key)


def transcribe_chunk(chunk_path: str) -> str:
    """
    Sends a single audio chunk to Groq's cloud-hosted Whisper LPU.
    Runs in 1-2 seconds per chunk.
    """
    client = get_groq_client()

    with open(chunk_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(chunk_path), file.read()),
            model="whisper-large-v3",
            response_format="text"
        )

    return transcription


def transcribe_all(chunks: list) -> str:
    """
    Loop through every audio chunk, send to Groq API, 
    and combine into a full transcript.
    """
    full_transcript = ""

    print("Using Groq Cloud API (whisper-large-v3) for instant transcription.")

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)} via Groq...")
        text = transcribe_chunk(chunk)
        full_transcript += text + " "

    print("Transcription complete.")
    return full_transcript.strip()