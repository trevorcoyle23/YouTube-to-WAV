#!/usr/bin/env python3
import argparse
import os
import sys
from yt_dlp import YoutubeDL

def download_wav(url: str, output: str = None, quiet: bool = False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(script_dir, "ffmpeg", "bin")

    if not os.path.exists(os.path.join(ffmpeg_path, "ffmpeg.exe")):
        raise FileNotFoundError(
            f"Could not find ffmpeg.exe in {ffmpeg_path}. "
            "Please place FFmpeg binaries in 'ffmpeg/bin' next to this script."
        )

    if output:
        out_dir = os.path.dirname(output) or "."
        stem = os.path.splitext(os.path.basename(output))[0]
        outtmpl = os.path.join(out_dir, stem + ".%(ext)s")
    else:
        outtmpl = "%(title)s.%(ext)s"

    ydl_opts = {
        "outtmpl": outtmpl,
        "quiet": quiet,
        "noprogress": quiet,
        "ffmpeg_location": ffmpeg_path,
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "0",
        }],
    }

    if not quiet:
        def hook(d):
            if d.get("status") == "downloading":
                eta = d.get("eta")
                speed = d.get("speed")
                percent = d.get("_percent_str", "").strip()
                sys.stdout.write(f"\rDownloading {percent}  "
                                 f"{(speed or 0)/1024:.0f} KiB/s  "
                                 f"ETA: {eta or '?'} s")
                sys.stdout.flush()
            elif d.get("status") == "finished":
                print("\nDownload complete. Converting to WAV...")
        ydl_opts["progress_hooks"] = [hook]

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        wav_path = ydl.prepare_filename(info)
        wav_path = os.path.splitext(wav_path)[0] + ".wav"
        return wav_path

def main():
    parser = argparse.ArgumentParser(
        description="Download the audio from a YouTube link as a WAV file."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-o", "--output", help="Output file path (e.g., out/music.wav)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Reduce console output")
    args = parser.parse_args()

    try:
        wav = download_wav(args.url, output=args.output, quiet=args.quiet)
        if not args.quiet:
            print(f"Saved WAV to: {wav}")
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()