"""Canvas LMS integration -- API client, file sync, and datastores.

DEPRECATED: This package uses a single shared CANVAS_API_TOKEN for all users,
which is a tenant-isolation issue. The tutor is now integrated into cs-navigator
as a sub-agent, where Canvas access is handled per-user by the backend
(LDAP auth + per-student DB storage). Do not use this package for multi-user
deployments. See: cs-chatbot-morganstate/adk_agent/cs_navigator_unified/sub_agents/tutor/
"""

from .client import CanvasClient
from .sync import sync_course_files, sync_all_courses
from .datastore import get_or_create_datastore
from .mapping import get_mapping, update_mapping

__all__ = [
    "CanvasClient",
    "sync_course_files",
    "sync_all_courses",
    "get_or_create_datastore",
    "get_mapping",
    "update_mapping",
]
