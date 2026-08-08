# ============================================================
# WHAT THIS FILE DOES (in one line):
# It takes the small WAV audio chunks (made by the other file)
# and turns them into TEXT, using Whisper — running locally,
# no internet call needed. English only.
# ============================================================

# whisper = OpenAI's speech-to-text library, runs locally on your computer
import whisper

# os = Python's built-in tool for working with folders, files, and
# "environment variables" (settings stored outside the code, e.g. in a .env file)
import os

# ------------------------------------------------------------
# SETTINGS / CONSTANTS
# ------------------------------------------------------------

# Which Whisper model size to use ("tiny", "small", "medium", "large").
# os.getenv("WHISPER_MODEL", "small") means:
# "look for an environment variable called WHISPER_MODEL —
#  if it's not set, just default to 'small'."
# Bigger models = more accurate but slower and use more memory.
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

# This variable will eventually hold the loaded Whisper model.
# It starts as "None" (empty/nothing) because we haven't loaded it yet.
# We only want to load it ONCE (loading is slow), then reuse it every time.
_model = None


def load_model():
    """
    Loads the Whisper model into memory — but only the FIRST time
    this function is called. Every time after that, it just hands back
    the already-loaded model instead of reloading it (which would be slow).
    This pattern is called "lazy loading" + "caching".
    """

    # "global _model" tells Python: "I want to change the _model variable
    # that lives OUTSIDE this function, not create a new local one."
    global _model

    # If we haven't loaded a model yet (_model is still None)...
    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")

    return _model


def transcribe_chunk(chunk_path: str) -> str:
    model = load_model()

    # Optimized for speed on CPU:
    result = model.transcribe(
        chunk_path, 
        task="transcribe", 
        fp16=False,
        beam_size=1,       # Reduces search path complexity (much faster)
        best_of=1,         # Prevents multiple sampling runs
        temperature=0.0    # Greedy decoding for max speed
    )

    return result["text"]


def transcribe_all(chunks: list) -> str:
    """
    The MAIN function of this file — takes the whole LIST of audio chunks
    (e.g. 6 chunks for a 1-hour meeting) and transcribes ALL of them,
    one by one, then joins everything into one big transcript string.
    """

    # This will hold the final combined transcript text for ALL chunks.
    full_transcript = ""

    print("Using Whisper for transcription.")

    # Loop through every chunk in the list, one at a time.
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk)

        # Add this chunk's text onto the running full transcript,
        # with a space so words from different chunks don't get glued together.
        full_transcript += text + " "

    print("Transcription complete.")

    # Remove any stray leading/trailing spaces and return the final,
    # complete transcript for the whole meeting.
    return full_transcript.strip()