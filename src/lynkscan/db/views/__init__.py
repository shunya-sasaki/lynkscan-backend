"""Views for the database."""

from lynkscan.db.views.software import SoftwareView
from lynkscan.db.views.vuln import VulnView

__all__ = [
    "SoftwareView",
    "VulnView",
]
