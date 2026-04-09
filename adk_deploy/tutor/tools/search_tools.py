"""Course material search using Vertex AI Discovery Engine directly.

We can't use VertexAiSearchTool here because datastores are only known at runtime
(created dynamically per-course). Instead we call the Discovery Engine SearchService.
"""

import os

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

from ..canvas.mapping import get_mapping

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
LOCATION = "us"


def _get_search_client():
    opts = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    return discoveryengine.SearchServiceClient(client_options=opts)


def search_course_materials(query: str, course_id: str) -> dict:
    """Search a course's Vertex AI Search datastore for relevant materials.

    Args:
        query: The search query (e.g., "linked list assignment", "midterm topics").
        course_id: The Canvas course ID to search within.

    Returns:
        A dict with search results including document snippets and extractive answers.
    """
    mapping = get_mapping()
    entry = mapping.get(str(course_id), {})
    datastore_id = entry.get("datastore_id")

    if not datastore_id:
        return {
            "status": "not_synced",
            "results": [],
            "message": (
                f"Course {course_id} hasn't been synced yet. "
                f"Ask the student to run sync_course_materials first."
            ),
        }

    client = _get_search_client()

    # Build the serving config path from the datastore ID
    # datastore_id looks like: projects/.../locations/.../collections/.../dataStores/canvas-course-123
    serving_config = f"{datastore_id}/servingConfigs/default_search"

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
            ),
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=3,
            ),
        ),
    )

    response = client.search(request)

    results = []
    for result in response.results:
        doc = result.document
        doc_data = {
            "title": doc.derived_struct_data.get("title", "Untitled") if doc.derived_struct_data else "Untitled",
            "snippets": [],
            "extractive_answers": [],
        }

        # Extract snippets
        if doc.derived_struct_data:
            snippets = doc.derived_struct_data.get("snippets", [])
            for s in snippets:
                if hasattr(s, "get"):
                    doc_data["snippets"].append(s.get("snippet", ""))
                else:
                    doc_data["snippets"].append(str(s))

            # Extract extractive answers
            answers = doc.derived_struct_data.get("extractive_answers", [])
            for a in answers:
                if hasattr(a, "get"):
                    doc_data["extractive_answers"].append(a.get("content", ""))
                else:
                    doc_data["extractive_answers"].append(str(a))

        results.append(doc_data)

    course_name = entry.get("course_name", f"Course {course_id}")
    return {
        "status": "ok",
        "course_name": course_name,
        "query": query,
        "result_count": len(results),
        "results": results,
    }
