"""Download the public ChatPRD Lenny transcript archive into data/transcripts."""

import io
import os
import zipfile
from pathlib import Path

import httpx

ARCHIVE_URL = os.getenv(
    "TRANSCRIPT_ARCHIVE_URL",
    "https://codeload.github.com/ChatPRD/lennys-podcast-transcripts/zip/refs/heads/main",
)
OUTPUT_DIR = Path(os.getenv("TRANSCRIPT_DIR", "data/transcripts"))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        response = client.get(ARCHIVE_URL)
        response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        members = [
            name
            for name in archive.namelist()
            if "/episodes/" in name and name.endswith("/transcript.md")
        ]
        if not members:
            raise RuntimeError("No episode transcript.md files found in archive")
        for member in members:
            relative = member.split("/episodes/", 1)[1]
            target = OUTPUT_DIR / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(member))

    print(f"Downloaded {len(members)} transcripts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
