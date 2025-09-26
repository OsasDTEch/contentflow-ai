import uuid
from auth.validate_users import get_current_user
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User
from database import models
from schemas.agent_schema import TargetAudience, CompanyProfile


def normalize_platforms(platforms):
    """Normalize platform data to list of strings"""
    if not platforms:
        return []
    if isinstance(platforms, list):
        return [str(p).lower() for p in platforms]
    return [str(platforms).lower()]


def normalize_content_prefs(prefs):
    """Normalize content preferences to list of strings"""
    if not prefs:
        return []
    if isinstance(prefs, dict):
        return list(prefs.keys())
    if isinstance(prefs, list):
        return [str(p) for p in prefs]
    return [str(prefs)]


def safe_get_list(data, default=None):
    """Safely get list data with fallback"""
    if default is None:
        default = []
    if not data:
        return default
    if isinstance(data, list):
        return data
    return default


async def get_company_profile(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> CompanyProfile:
    """Get company profile for authenticated user"""
    try:
        # Get company
        company = db.query(models.Company).filter(
            models.Company.creator_id == user.id
        ).first()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Get related data
        brand_profile = db.query(models.BrandProfile).filter(
            models.BrandProfile.company_id == company.id
        ).first()

        target_audience = db.query(models.TargetAudience).filter(
            models.TargetAudience.company_id == company.id
        ).first()

        content_themes = db.query(models.ContentTheme).filter(
            models.ContentTheme.company_id == company.id
        ).all()

        competitors = db.query(models.Competitor).filter(
            models.Competitor.company_id == company.id
        ).all()

        # Extract competitor domains
        competitor_domains = []
        for comp in competitors:
            if comp.domain:
                competitor_domains.append(comp.domain)

        # Build target audience data
        if target_audience:
            audience_data = TargetAudience(
                name=target_audience.name or "Primary Audience",
                pain_points=safe_get_list(target_audience.pain_points),
                demographics=safe_get_list(target_audience.company_sizes),
                preferred_platforms=normalize_platforms(target_audience.preferred_platforms),
                content_preferences=normalize_content_prefs(
                    brand_profile.preferred_content_formats if brand_profile else None
                ),
                engagement_patterns=safe_get_list(target_audience.engagement_triggers)
            )
        else:
            # Fallback audience
            audience_data = TargetAudience(
                name="General Audience",
                pain_points=["Generic business challenges"],
                demographics=["Business professionals"],
                preferred_platforms=["linkedin"],
                content_preferences=["blog_posts"],
                engagement_patterns=["weekday_engagement"]
            )

        # Get company settings
        settings = company.settings or {}
        business_objectives = settings.get("business_objectives", ["Increase brand awareness"])

        return CompanyProfile(
            company_id=company.id,
            company_name=company.name,
            industry=company.industry,
            target_audience=audience_data,
            content_themes=[theme.name for theme in content_themes] or ["Industry Updates"],
            competitor_domains=competitor_domains,
            business_objectives=business_objectives,
            brand_voice=brand_profile.brand_voice if brand_profile else "Professional",
            content_preferences=normalize_content_prefs(
                brand_profile.preferred_content_formats if brand_profile else ["blog_posts"]
            ),
            posting_frequency_target=3,
            seo_keywords=safe_get_list(
                content_themes[0].keywords if content_themes else None,
                ["industry keywords"]
            ),
            budget_constraints=None,
            content_restrictions=safe_get_list(
                brand_profile.topics_to_avoid if brand_profile else None
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building company profile: {str(e)}")