"""
Analysis module for UHI-LST insights generation.

This module provides AI-powered analysis and recommendations
based on calculated indices and statistics.
"""

from .insights import (
    generate_insights,
    generate_explanation,
    generate_recommendations,
    UHISeverity,
    Recommendation,
)

__all__ = [
    "generate_insights",
    "generate_explanation",
    "generate_recommendations",
    "UHISeverity",
    "Recommendation",
]
