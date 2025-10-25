"""Minimal justification schema for pre-execution reflection."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ConfidenceLevel = Literal["low", "medium", "high"]


class Alternative(BaseModel):
    """An alternative method that was considered but rejected."""

    method: str = Field(..., description="Name of the alternative method")
    why_not: str = Field(..., description="Reason for rejection")


class Choice(BaseModel):
    """The selected method with rationale."""

    method: str = Field(..., description="Name of the selected method")
    rationale: str = Field(..., description="Why this method fits the intent")
    tradeoffs: str = Field(..., description="Known limitations or compromises")


class Justification(BaseModel):
    """Minimal justification structure for consequential operations."""

    intent: str = Field(..., description="What property must be preserved")
    alternatives: list[Alternative] = Field(
        default_factory=list,
        description="Methods considered but rejected",
    )
    choice: Choice = Field(..., description="Selected method with rationale")
    confidence: ConfidenceLevel = Field(..., description="Confidence level in this choice")


# Alias for backward compatibility during migration
EpistemicJustification = Justification
