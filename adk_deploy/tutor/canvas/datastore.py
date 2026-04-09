"""Create and manage per-course Vertex AI Search datastores."""

import os

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

from .mapping import get_mapping, update_mapping

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
LOCATION = "us"  # Discovery Engine datastores live in "us" or "eu"
BUCKET_NAME = os.getenv("GCS_BUCKET", "ai-agent-csdept-1")
COLLECTION = "default_collection"


def _get_client():
    opts = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    return discoveryengine.DataStoreServiceClient(client_options=opts)


def _get_doc_client():
    opts = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    return discoveryengine.DocumentServiceClient(client_options=opts)


def get_or_create_datastore(course_id: str, course_name: str) -> str:
    """Return an existing datastore ID for the course, or create a new one.

    Returns the full datastore resource path.
    """
    mapping = get_mapping()
    entry = mapping.get(str(course_id), {})

    datastore_id = f"canvas-course-{course_id}"

    if entry.get("datastore_id"):
        return entry["datastore_id"]

    # Create the datastore
    client = _get_client()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}"

    datastore = discoveryengine.DataStore(
        display_name=f"Canvas: {course_name}",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )

    operation = client.create_data_store(
        parent=parent,
        data_store=datastore,
        data_store_id=datastore_id,
    )

    # Wait for creation to complete
    result = operation.result(timeout=120)
    full_id = result.name

    # Update mapping with the datastore ID
    entry["datastore_id"] = full_id
    entry["course_name"] = course_name
    update_mapping(str(course_id), entry)

    return full_id


def import_documents(course_id: str) -> str:
    """Import documents from GCS into the course's datastore.

    Returns the operation name for status checking.
    """
    mapping = get_mapping()
    entry = mapping.get(str(course_id), {})
    datastore_id = entry.get("datastore_id")
    if not datastore_id:
        raise ValueError(f"No datastore found for course {course_id}. Run get_or_create_datastore first.")

    client = _get_doc_client()

    # The branch is always "default_branch" for unstructured docs
    parent = f"{datastore_id}/branches/default_branch"

    gcs_source = discoveryengine.GcsSource(
        input_uris=[f"gs://{BUCKET_NAME}/course_files/{course_id}/*"],
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=gcs_source,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    operation = client.import_documents(request=request)
    return operation.operation.name


def check_import_status(operation_name: str) -> dict:
    """Check the status of a document import LRO."""
    from google.api_core import operations_v1
    from google.api_core.client_options import ClientOptions as CO

    opts = CO(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    ops_client = operations_v1.OperationsClient(
        channel=None,
    )
    # Use the discovery engine transport instead
    client = _get_doc_client()
    op = client.transport.operations_client.get_operation(operation_name)
    return {
        "done": op.done,
        "name": op.name,
        "error": str(op.error) if op.error.code else None,
    }
