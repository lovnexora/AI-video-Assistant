# # ============================================================
# # WHAT THIS FILE DOES (in one line):
# # It takes either a YouTube link OR a local audio/video file,
# # turns it into a clean WAV audio file, and then cuts that WAV
# # file into smaller pieces (chunks) so it's easier to transcribe later.
# # ============================================================

# # yt_dlp = a tool that can download audio/video from YouTube (and many other sites)
# import yt_dlp

# # AudioSegment = a tool from the "pydub" library that lets us open, edit,
# # and save audio files easily (like cutting, converting formats, etc.)
# from pydub import AudioSegment

# # os = Python's built-in tool for working with folders and file paths
# import os

# # This is the name of the folder where downloaded audio will be saved.
# # NOTE: this is spelled "downloades" (typo) — it will still work fine,
# # Python doesn't care about the spelling, it just creates a folder with this exact name.
# DOWNLOAD_DIR = 'downloades'

# # This line creates that folder if it doesn't already exist.
# # exist_ok=True means: "if the folder is already there, don't crash, just continue."
# os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# def download_youtube_audio(url: str) -> str:
#     """
#     This function's job: give it a YouTube URL, it downloads
#     just the AUDIO (not video) and saves it as a .wav file.
#     It returns the file path of the saved audio.
#     """

#     # This builds the path/name pattern for the downloaded file.
#     # "%(title)s.%(ext)s" is a placeholder — yt_dlp will automatically
#     # replace %(title)s with the video's real title, and %(ext)s with
#     # the real file extension (like .webm or .m4a) once it knows them.
#     output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

#     # This dictionary is basically a "settings sheet" that tells yt_dlp
#     # exactly HOW we want the download to happen.
#     ydl_opts = {
#         # "format": which version of the video/audio to grab.
#         # "bestaudio/best" means: "give me the best pure-audio version,
#         # but if that's not available, just give me the best overall version."
#         "format": "bestaudio/best",

#         # Where to save the file, using the pattern we built above.
#         "outtmpl": output_path,

#         # postprocessors = extra steps to run AFTER downloading.
#         # Here we tell it: "after downloading, convert whatever you got
#         # into a WAV audio file."
#         "postprocessors": [
#             {
#                 "key": "FFmpegExtractAudio",   # use FFmpeg to pull out just the audio
#                 "preferredcodec": "wav",        # convert that audio into .wav format
#                 "preferredquality": "192",      # audio quality setting (192 kbps)
#             }
#         ],

#         # quiet=True means: don't print a ton of download progress messages
#         # to the screen. Keeps things clean.
#         "quiet": True,
#     }

#     # This actually creates the downloader tool using our settings above,
#     # and "with ... as ydl" makes sure it cleans up properly when done.
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:

#         # This does the real work: it downloads the video/audio from the URL,
#         # and "info" ends up holding details about what was downloaded
#         # (title, format, file extension, etc.)
#         info = ydl.extract_info(url, download=True)

#         # yt_dlp can tell us what filename it actually used, based on "info".
#         # BUT: even though we asked for .wav in postprocessors, the filename
#         # yt_dlp predicts here might still show the ORIGINAL extension
#         # (like .webm or .m4a) because that's what it downloaded before converting.
#         # So these two ".replace()" calls manually fix the filename text
#         # to say ".wav" instead, to match what the file actually became.
#         filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")

#     # Send back the final file path so other code can use it.
#     return filename


# def convert_to_wav(input_path: str) -> str:
#     """
#     This function's job: take ANY local audio or video file
#     (mp3, mp4, m4a, whatever) and convert it into a clean WAV file
#     that's ready for transcription.
#     """

#     # Build the output filename by taking the original path,
#     # removing its extension (like .mp4), and adding "_converted.wav" instead.
#     # Example: "meeting.mp4" becomes "meeting_converted.wav"
#     output_path = os.path.splitext(input_path)[0] + "_converted.wav"

#     # Open/load the original file using pydub. Pydub uses FFmpeg behind
#     # the scenes, so it can read almost any audio or video format.
#     audio = AudioSegment.from_file(input_path)

#     # set_channels(1) = convert to MONO (single audio channel, not stereo).
#     # set_frame_rate(16000) = convert to 16,000 Hz sample rate.
#     # WHY: speech-to-text models (like Whisper) expect mono, 16kHz audio —
#     # this is basically "preparing the audio the way the transcriber wants it."
#     audio = audio.set_channels(1).set_frame_rate(16000)  # 16khz

#     # Save (export) this cleaned-up audio as a real .wav file on disk.
#     audio.export(output_path, format="wav")

#     # Send back the path of this new, converted file.
#     return output_path


# def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
#     """
#     This function's job: take one big WAV file and slice it into
#     smaller pieces (chunks), each "chunk_minutes" long (10 minutes by default).
#     WHY: transcribing one giant file at once can be slow, use too much memory,
#     or hit size limits — smaller pieces are easier and safer to process.
#     """

#     # Load the full WAV file into memory using pydub.
#     audio = AudioSegment.from_wav(wav_path)

#     # pydub measures audio length in MILLISECONDS, not minutes.
#     # So we convert: minutes -> seconds -> milliseconds.
#     chunk_ms = chunk_minutes * 60 * 1000

#     # This list will collect the file paths of every chunk we create.
#     chunks = []

#     # len(audio) = total length of the audio in milliseconds.
#     # range(0, len(audio), chunk_ms) walks through the audio in steps of
#     # chunk_ms — so if chunk_ms = 10 minutes, it jumps 0, 10min, 20min, 30min...
#     # enumerate(...) also gives us "i" = 0, 1, 2, 3... to number each chunk.
#     for i, start in enumerate(range(0, len(audio), chunk_ms)):

#         # Slice out just this piece of audio, from "start" to "start + chunk_ms".
#         # (If there's less than chunk_ms left at the end, pydub just gives
#         # whatever remains — it won't crash or add silence.)
#         chunk = audio[start: start + chunk_ms]

#         # Build a filename for this chunk, like "meeting.wav_chunk_0.wav"
#         chunk_path = f"{wav_path}_chunk_{i}.wav"

#         # Save this small piece as its own WAV file.
#         chunk.export(chunk_path, format="wav")

#         # Add this chunk's file path to our running list.
#         chunks.append(chunk_path)

#     # Once all chunks are made, send back the full list of chunk file paths.
#     return chunks


# def process_input(source: str) -> list:
#     """
#     This is the MAIN function that ties everything together.
#     You give it either:
#       - a YouTube URL (starts with http:// or https://), OR
#       - a path to a local file on your computer
#     And it returns a list of small WAV audio chunks, ready to be transcribed.
#     """

#     # Check if "source" looks like a web link (starts with http:// or https://).
#     if source.startswith("http://") or source.startswith("https://"):
#         print("Detected YouTube URL. Downloading audio...")
#         # It's a URL, so download the audio from it.
#         wav_path = download_youtube_audio(source)
#     else:
#         print("Detected local file. Converting to WAV...")
#         # It's not a URL, so treat it as a local file and convert it.
#         wav_path = convert_to_wav(source)

#     print("Chunking audio...")
#     # Whether it came from YouTube or a local file, we now have ONE wav file.
#     # Cut that wav file into smaller chunks.
#     chunks = chunk_audio(wav_path)

#     print(f"Audio ready — {len(chunks)} chunk(s) created.")

#     # Return the final list of chunk file paths — this is what the rest
#     # of your program (e.g. the transcription step) will use next.
#     return chunks

import os
import sys
import yt_dlp
from pydub import AudioSegment
import static_ffmpeg

# ============================================================
# BULLETPROOF FFMPEG & FFPROBE AUTO-SETUP
# ============================================================
# Automatically downloads binaries (if needed) and adds them to os.environ["PATH"]
static_ffmpeg.add_paths()

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Downloads YouTube audio using yt-dlp with auto-linked binaries.
    """
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        base_name, _ = os.path.splitext(filename)
        wav_filename = f"{base_name}.wav"

    return wav_filename


def convert_to_wav(input_path: str) -> str:
    """
    Converts local media file into 16kHz mono WAV format.
    """
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 3) -> list:
    """Slices WAV file into smaller 3-minute chunks for faster CPU processing."""
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    """
    Main pipeline entry function.
    """
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks