"""
domains/__init__.py - ENTERPRISE DOMAINS
========================================
Domain-Driven Design implementation for Conecta PRO ERP

Available Domains:
- procurement: Enterprise procurement and contract management
- financial: Double-entry accounting and financial operations
- hr: Human resources with Brazilian labor law compliance
- inventory: Product and stock management
"""

from . import financial, hr, inventory, procurement

__all__ = ["procurement", "financial", "hr", "inventory"]
