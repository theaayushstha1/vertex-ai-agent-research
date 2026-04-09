"""Course-to-datastore mapping stored in GCS as JSON."""

import json
import os

from google.cloud import storage

BUCKET_NAME = os.getenv("GCS_BUCKET", "ai-agent-csdept-1")
MAPPING_BLOB = "course_datastores/mapping.json"


def _get_bucket():
    client = storage.Client()
    return client.bucket(BUCKET_NAME)


def get_mapping() -> dict:
    """Read the course -> datastore mapping from GCS.

    Returns dict of {course_id: {datastore_id, course_name, last_synced, file_count}}.
    """
    bucket = _get_bucket()
    blob = bucket.blob(MAPPING_BLOB)
    if not blob.exists():
        return {}
    data = blob.download_as_text()
    return json.loads(data)


def update_mapping(course_id: str, entry: dict) -> None:
    """Update one course entry in the mapping, using generation preconditions for safety."""
    bucket = _get_bucket()
    blob = bucket.blob(MAPPING_BLOB)

    # Read current version
    current = {}
    generation = 0
    if blob.exists():
        blob.reload()
        generation = blob.generation
        current = json.loads(blob.download_as_text())

    current[str(course_id)] = entry

    # Write back with generation precondition to avoid clobbering concurrent writes
    blob.upload_from_string(
        json.dumps(current, indent=2),
        content_type="application/json",
        if_generation_match=generation,
    )
