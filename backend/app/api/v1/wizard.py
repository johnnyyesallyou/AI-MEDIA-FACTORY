"""Sprint 68.1: Wizard API with LLM-based theme classification."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.engines.theme_classifier import ThemeClassifier

router = APIRouter(prefix="/wizard", tags=["wizard"])

classifier = ThemeClassifier()


class WizardSuggestRequest(BaseModel):
    description: str = Field(min_length=3, max_length=1000)


class WizardSuggestResponse(BaseModel):
    theme: str
    niche: str
    archetype: str
    tone: str
    risk_level: str
    suggested_template: Optional[str] = None
    publishing_mode: str


@router.post("/suggest", response_model=WizardSuggestResponse)
async def wizard_suggest(request: WizardSuggestRequest):
    """
    Sprint 68.1: LLM-based channel theme classification.
    
    User writes description → AI analyzes → returns theme/niche/archetype/tone/risk.
    """
    # Classify using LLM
    classification = classifier.classify(request.description)
    
    # Map archetype to template name
    archetype_to_template = {
        "news": "news",
        "releases": "releases",
        "educational": "educational",
        "entertainment": "community",
        "viral": "viral",
        "reviews": "reviews",
        "community": "community",
        "aggregator": "news",
    }
    suggested_template = archetype_to_template.get(classification["archetype"], "news")
    
    # Map risk_level to publishing_mode
    risk_to_mode = {
        "low": "auto",
        "medium": "approval_required",
        "high": "approval_required",
    }
    publishing_mode = risk_to_mode.get(classification["risk_level"], "approval_required")
    
    return WizardSuggestResponse(
        theme=classification["theme"],
        niche=classification["niche"],
        archetype=classification["archetype"],
        tone=classification["tone"],
        risk_level=classification["risk_level"],
        suggested_template=suggested_template,
        publishing_mode=publishing_mode,
    )