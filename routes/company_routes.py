from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User
from database.schemas import UserLogin, UserCreate, TokenResponse
from database import schemas,models
from auth.validate_users import get_current_user
from utils.generate_uuid import generate_company_uuid, generate_uuid


router = APIRouter(prefix="/company", tags=["company"])
@router.post('/add_company_info', response_model=schemas.CompanyCreateResponse)
async def add_company_info(company:schemas.CompanyCreate, user: User= Depends(get_current_user), db: Session = Depends(get_db)):

    existing_company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()
    if existing_company:
        raise HTTPException(status_code=400, detail="User already created a company")
    new_company = models.Company(
        id=generate_uuid(),
        name=company.name,
        domain=company.domain,
        industry=company.industry,
        company_size=company.company_size,
        description= company.description,
        website_url=company.website_url,
        creator_id=user.id,
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    new_member= models.CompanyMember(
        id=generate_uuid(),
        user_id= user.id,
        company_id=new_company.id,
        role='admin',
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return schemas.CompanyCreateResponse(
        status=status.HTTP_201_CREATED,
        message="Company created successfully",
        data=schemas.CompanyResponse(
            id=new_company.id,
            name=new_company.name,
            domain=new_company.domain,
            company_size=new_company.company_size,
            description=new_company.description,
            industry=new_company.industry,
            subscription_tier=new_company.subscription_tier,
            onboarding_step=new_company.onboarding_step,
            onboarding_completed=new_company.onboarding_completed,
            created_at=new_company.created_at,
            creator_id=new_company.creator_id,
        )
    )

@router.get("/my_company", response_model=schemas.CompanyCreateResponse)
async def get_my_company(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.creator_id == user.id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return schemas.CompanyCreateResponse(
        status=status.HTTP_200_OK,
        message="Company retrieved successfully",
        data=schemas.CompanyResponse(
            id=company.id,
            name=company.name,
            domain=company.domain,
            company_size=company.company_size,
            description=company.description,
            industry=company.industry,
            subscription_tier=company.subscription_tier,
            onboarding_step=company.onboarding_step,
            onboarding_completed=company.onboarding_completed,
            created_at=company.created_at,
            creator_id=company.creator_id,
        )
    )


