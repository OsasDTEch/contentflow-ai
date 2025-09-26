import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas, models
from utils.generate_uuid import generate_company_uuid, generate_uuid, generate_member_uuid
from auth.validate_users import get_current_user

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# ============================================================================
# ONBOARDING STEP 1: COMPANY BASIC INFORMATION
# ============================================================================
@router.post("/step1", response_model=schemas.OnboardingResponse)
async def add_onboarding_step1(
        step1: schemas.OnboardingStep1,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if user already has a company
    existing_company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if existing_company:
        raise HTTPException(status_code=400, detail="User already has a company profile")

    # Create new company
    new_company = models.Company(
        id=generate_uuid(),
        name=step1.company_name,
        industry=step1.industry,
        company_size=step1.company_size,
        website_url=step1.website_url,
        description=step1.description,
        creator_id=user.id,
        subscription_tier=models.SubscriptionTier.STARTER,  # Use enum
        settings={}  # Initialize empty settings
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return schemas.OnboardingResponse(
        message="Company profile created successfully",
        data={"company_id": str(new_company.id), "company_name": new_company.name}
    )


# ============================================================================
# ONBOARDING STEP 2: BRAND PROFILE & VOICE
# ============================================================================
@router.post("/step2", response_model=schemas.OnboardingResponse)
async def add_onboarding_step2(
        step2: schemas.OnboardingStep2,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Get user's company
    existing_company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if not existing_company:
        raise HTTPException(status_code=400, detail="Complete step 1 first")

    # Check if brand profile already exists
    existing_brand_profile = db.query(models.BrandProfile).filter(
        models.BrandProfile.company_id == existing_company.id
    ).first()
    if existing_brand_profile:
        raise HTTPException(status_code=400, detail="Brand profile already exists")

    # Create brand profile
    new_brand_profile = models.BrandProfile(
        id=generate_uuid(),
        company_id=existing_company.id,
        brand_voice=step2.brand_voice,
        brand_personality_traits=step2.brand_personality_traits,
        core_values=step2.core_values,
        unique_value_proposition=step2.unique_value_proposition,
        content_tone_preferences=step2.content_tone_preferences,
        topics_to_avoid=step2.topics_to_avoid,
        preferred_content_formats=step2.preferred_content_formats,
    )

    db.add(new_brand_profile)
    db.commit()
    db.refresh(new_brand_profile)

    return schemas.OnboardingResponse(
        message="Brand profile added successfully",
        data={"brand_profile_id": str(new_brand_profile.id)}
    )


# ============================================================================
# ONBOARDING STEP 3: TARGET AUDIENCES
# ============================================================================
@router.post("/step3", response_model=schemas.OnboardingResponse)
async def add_onboarding_step3(
        step3: schemas.OnboardingStep3,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Get user's company
    company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Complete step 1 first")

    # Check if audiences already exist
    existing_audiences = db.query(models.TargetAudience).filter(
        models.TargetAudience.company_id == company.id
    ).first()
    if existing_audiences:
        raise HTTPException(status_code=400, detail="Target audiences already exist")

    # Validate only one primary audience
    primary_count = sum(1 for audience in step3.audiences if audience.is_primary)
    if primary_count != 1:
        raise HTTPException(status_code=400, detail="Exactly one audience must be marked as primary")

    # Create target audiences one by one to avoid batch insert issues
    created_audiences = []
    try:
        for audience in step3.audiences:
            new_audience = models.TargetAudience(
                id=generate_uuid(),
                company_id=company.id,
                name=audience.name,
                is_primary=audience.is_primary,
                job_titles=audience.job_titles,
                industries=audience.industries,
                company_sizes=audience.company_sizes,
                pain_points=audience.pain_points,
                goals_objectives=audience.goals_objectives,
                preferred_platforms=audience.preferred_platforms
            )

            db.add(new_audience)
            db.commit()  # Commit each record individually
            db.refresh(new_audience)
            created_audiences.append(new_audience)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create audiences: {str(e)}")

    return schemas.OnboardingResponse(
        message="Target audiences added successfully",
        data={"audiences_created": len(created_audiences)}
    )


# ============================================================================
# ONBOARDING STEP 4: CONTENT STRATEGY & GOALS
# ============================================================================
@router.post("/step4", response_model=schemas.OnboardingResponse)
async def add_onboarding_step4(
        step4: schemas.OnboardingStep4,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Complete step 1 first")

    # Validate content mix percentages
    if sum(step4.content_mix_preferences.values()) != 100:
        raise HTTPException(status_code=400, detail="Content mix percentages must total 100%")

    # Prevent duplicate themes
    if db.query(models.ContentTheme).filter(models.ContentTheme.company_id == company.id).first():
        raise HTTPException(status_code=400, detail="Content themes already exist")

    # Save strategy to company settings
    current_settings = company.settings or {}
    current_settings.update({
        "business_objectives": step4.business_objectives,
        "target_keywords": step4.target_keywords,
        "posting_frequency_preferences": step4.posting_frequency_preferences,
        "content_mix_preferences": step4.content_mix_preferences
    })
    company.settings = current_settings
    db.add(company)

    # Create content themes
    created_themes = []
    try:
        for theme in step4.content_themes:
            new_theme = models.ContentTheme(
                id=generate_uuid(),
                company_id=company.id,
                name=theme.name,
                description=theme.description or "",
                keywords=getattr(theme, "keywords", []),
                priority_score=getattr(theme, "priority_score", 50),
                is_evergreen=getattr(theme, "is_evergreen", True)
            )
            db.add(new_theme)
            db.commit()
            db.refresh(new_theme)
            created_themes.append(new_theme)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create themes: {str(e)}")

    return schemas.OnboardingResponse(
        message="Content strategy and themes added successfully",
        data={"themes_created": len(created_themes)}
    )


# ============================================================================
# ONBOARDING STEP 5: COMPETITIVE INTELLIGENCE
# ============================================================================
@router.post("/step5", response_model=schemas.OnboardingResponse)
async def add_onboarding_step5(
        step5: schemas.OnboardingStep5,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Complete step 1 first")

    if db.query(models.Competitor).filter(models.Competitor.company_id == company.id).first():
        raise HTTPException(status_code=400, detail="Competitors already exist")

    # Update company settings with competitive advantages
    current_settings = company.settings or {}
    current_settings["competitive_advantages"] = step5.competitive_advantages
    company.settings = current_settings
    db.add(company)

    # Create competitors
    created_competitors = []
    try:
        for competitor in step5.competitors:
            new_comp = models.Competitor(
                id=generate_uuid(),
                company_id=company.id,
                name=competitor.name,
                domain=competitor.domain,
                description=competitor.description,
                social_profiles=competitor.social_profiles or {},
                content_analysis_enabled=True
            )
            db.add(new_comp)
            db.commit()
            db.refresh(new_comp)
            created_competitors.append(new_comp)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create competitors: {str(e)}")

    return schemas.OnboardingResponse(
        message="Competitive intelligence added successfully",
        data={"competitors_created": len(created_competitors)}
    )


# ============================================================================
# ONBOARDING STEP 6: PLATFORM INTEGRATIONS
# ============================================================================
@router.post("/step6", response_model=schemas.OnboardingResponse)
async def add_onboarding_step6(
        step6: schemas.OnboardingStep6,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Complete step 1 first")

    if db.query(models.PlatformIntegration).filter(models.PlatformIntegration.company_id == company.id).first():
        raise HTTPException(status_code=400, detail="Platform integrations already exist")

    # Update company settings
    current_settings = company.settings or {}
    current_settings.update({
        "timezone": step6.timezone,
        "automation_preferences": step6.automation_preferences,
        "content_review_required": step6.content_review_required
    })
    company.settings = current_settings

    # Create integrations
    created_integrations = []
    try:
        for platform_name in step6.platforms_to_connect:
            new_integration = models.PlatformIntegration(
                id=generate_uuid(),
                company_id=company.id,
                platform_name=platform_name.lower(),
                is_enabled=True,
                is_connected=False,
                sync_status="pending"
            )
            db.add(new_integration)
            db.commit()
            db.refresh(new_integration)
            created_integrations.append(new_integration)

        # Mark onboarding complete
        company.onboarding_completed = True
        company.onboarding_step = 6
        db.add(company)
        db.commit()
        db.refresh(company)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create integrations: {str(e)}")

    return schemas.OnboardingResponse(
        message="Platform integrations configured and onboarding completed!",
        data={
            "integrations_created": len(created_integrations),
            "onboarding_completed": True,
            "company_id": str(company.id)
        }
    )


# ============================================================================
# ONBOARDING STATUS CHECK
# ============================================================================
@router.get("/status", response_model=schemas.OnboardingResponse)
async def get_onboarding_status(
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Get user's company
    company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()

    if not company:
        return schemas.OnboardingResponse(
            message="Onboarding not started",
            data={"step": 0, "completed": False}
        )

    # Check which steps are completed
    steps_completed = {
        "step1": bool(company),
        "step2": bool(db.query(models.BrandProfile).filter(models.BrandProfile.company_id == company.id).first()),
        "step3": bool(db.query(models.TargetAudience).filter(models.TargetAudience.company_id == company.id).first()),
        "step4": bool(db.query(models.ContentTheme).filter(models.ContentTheme.company_id == company.id).first()),
        "step5": bool(db.query(models.Competitor).filter(models.Competitor.company_id == company.id).first()),
        "step6": bool(company.onboarding_completed)
    }

    # Calculate current step
    current_step = 1
    for step, completed in steps_completed.items():
        if completed:
            current_step = int(step[-1]) + 1
        else:
            break

    return schemas.OnboardingResponse(
        message="Onboarding status retrieved",
        data={
            "current_step": min(current_step, 6),
            "steps_completed": steps_completed,
            "onboarding_completed": company.onboarding_completed if company else False
        }
    )