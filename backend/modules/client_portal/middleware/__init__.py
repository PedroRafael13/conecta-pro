"""Middleware do Portal do Cliente."""

from .portal_auth import get_current_portal_client

__all__ = ["get_current_portal_client"]
