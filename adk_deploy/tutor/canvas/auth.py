"""Canvas LMS authentication via personal access token."""

import os

CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN", "")
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL", "https://morganstate.instructure.com")
