"""Download files from Canvas and upload to GCS for indexing."""

import os
from datetime import datetime, timezone

from google.cloud import storage

from .client import CanvasClient
from .mapping import update_mapping

BUCKET_NAME = os.getenv("GCS_BUCKET", "ai-agent-csdept-1")
SUPPORTED_TYPES = {"pdf", "docx", "pptx", "txt", "html"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


async def sync_course_files(client: CanvasClient, course_id: int, course_name: str) -> dict:
    """Download supported files from a Canvas course and upload to GCS.

    Returns a summary dict with file_count and any skipped files.
    """
    files = await client.get_course_files(course_id)
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(BUCKET_NAME)

    uploaded = 0
    skipped = []

    for f in files:
        ext = _extension(f.get("display_name", ""))
        size = f.get("size", 0)

        if ext not in SUPPORTED_TYPES:
            skipped.append(f"Unsupported type: {f['display_name']}")
            continue
        if size > MAX_FILE_SIZE:
            skipped.append(f"Too large (>{MAX_FILE_SIZE // (1024*1024)}MB): {f['display_name']}")
            continue

        # Download from Canvas
        content = await client.download_file(f["url"])
        if content is None:
            skipped.append(f"Download failed: {f['display_name']}")
            continue

        # Upload to GCS under course-specific path
        blob_path = f"course_files/{course_id}/{f['display_name']}"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(content)
        uploaded += 1

    # Update mapping
    update_mapping(str(course_id), {
        "course_name": course_name,
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "file_count": uploaded,
    })

    return {
        "course_id": course_id,
        "course_name": course_name,
        "files_uploaded": uploaded,
        "files_skipped": len(skipped),
        "skip_reasons": skipped[:10],  # cap for readability
    }


async def sync_all_courses(client: CanvasClient) -> list[dict]:
    """Sync files for every active enrollment."""
    enrollments = await client.get_current_enrollments()
    results = []
    for enrollment in enrollments:
        course_id = enrollment["course_id"]
        # Fetch course name
        info = await client.get_course_info(course_id)
        course_name = info.get("name", f"Course {course_id}")
        result = await sync_course_files(client, course_id, course_name)
        results.append(result)
    return results
