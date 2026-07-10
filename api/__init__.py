"""
api package
===========
Production FastAPI server package for Ops Brain Local.
Exports the main FastAPI application instance.
"""

from api.app import app

__all__ = ["app"]
