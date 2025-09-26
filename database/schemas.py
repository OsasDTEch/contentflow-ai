from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class CompanySize(str, Enum):
    STARTUP = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1000+"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# ============================================================================
# BASE RESPONSE MODELS
# ============================================================================

class BaseResponse(BaseModel):
    success: bool
    message: str
    status_code: int


class SuccessResponse(BaseResponse):
    success: bool = True
    status_code: int = 200
    message:str = "success"
    data: Optional[Any] = None


class ErrorResponse(BaseResponse):
    success: bool = False
    error_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(ErrorResponse):
    status_code: int = 422
    error_type: str = "validation_error"
    validation_errors: List[Dict[str, str]]


# ============================================================================
# USER AUTHENTICATION SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id:uuid.UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreateResponse(SuccessResponse):
    status_code: int = 201
    message: str = "User created successfully."
    data: UserResponse


class UserLoginResponse(SuccessResponse):
    message: str = "Login successful"
    data: Dict[str, Any]  # Contains user data and access token


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# COMPANY & ONBOARDING SCHEMAS
# ============================================================================

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    industry: str = Field(..., max_length=100)
    company_size: CompanySize
    description: Optional[str] = None
    website_url: Optional[str] = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    industry: str
    company_size: CompanySize
    subscription_tier: SubscriptionTier
    onboarding_completed: bool
    onboarding_step: int
    created_at: datetime
    creator_id:uuid.UUID

    class Config:
        from_attributes = True


class CompanyCreateResponse(SuccessResponse):
    status_code: int = 201
    message: str = "Company created successfully"
    data: CompanyResponse


# ============================================================================
# ONBOARDING SCHEMAS
# ============================================================================

class OnboardingStep1(BaseModel):
    """Company Basic Information"""
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=100)
    company_size: CompanySize
    website_url: Optional[str] = None
    description: Optional[str] = None


class OnboardingStep2(BaseModel):
    """Brand Profile & Voice"""
    brand_voice: str = Field(..., description="Professional, Casual, Authoritative, Friendly")
    brand_personality_traits: List[str] = Field(..., max_items=5)
    core_values: List[str] = Field(..., max_items=5)
    unique_value_proposition: str = Field(..., max_length=500)
    content_tone_preferences: Dict[str, int] = Field(..., description="Percentages for formal/casual")
    topics_to_avoid: List[str] = Field(default_factory=list, max_items=10)
    preferred_content_formats: List[str] = Field(..., min_items=1)


class AudienceData(BaseModel):
    name: str
    is_primary: bool = False
    job_titles: List[str]
    industries: List[str]
    company_sizes: List[str]
    pain_points: List[str]
    goals_objectives: List[str]
    preferred_platforms: List[str]


class OnboardingStep3(BaseModel):
    """Target Audience"""
    audiences: List[AudienceData] = Field(..., min_items=1, max_items=5)



from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# Step 4: Content Strategy & Goals
class ContentTheme(BaseModel):
    name: str
    description: Optional[str] = None
    priority: Optional[str] = None  # e.g., High, Medium, Low

class OnboardingStep4(BaseModel):
    business_objectives: List[str] = Field(..., min_items=1)
    content_themes: List[ContentTheme] = Field(..., min_items=3, max_items=10)
    target_keywords: List[str] = Field(..., min_items=5, max_items=20)
    posting_frequency_preferences: Dict[str, str]  # e.g., {"LinkedIn": "3/week"}
    content_mix_preferences: Dict[str, int]  # e.g., {"Blog": 30, "Video": 70}

# Step 5: Competitive Intelligence
class CompetitorData(BaseModel):
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    social_profiles: Dict[str, str] = Field(default_factory=dict)

class OnboardingStep5(BaseModel):
    competitors: List[CompetitorData] = Field(..., min_items=1, max_items=10)
    competitive_advantages: List[str] = Field(..., min_items=1)

# Step 6: Platform Integrations
class OnboardingStep6(BaseModel):
    platforms_to_connect: List[str] = Field(..., min_items=1)
    timezone: str = Field(default="UTC")
    automation_preferences: Dict[str, str] = Field(..., description="Platform: automation setting")
    content_review_required: bool = True


class OnboardingComplete(BaseModel):
    """Final onboarding data compilation"""
    step1: OnboardingStep1
    step2: OnboardingStep2
    step3: OnboardingStep3
    step4: OnboardingStep4
    step5: OnboardingStep5
    step6: OnboardingStep6


class OnboardingResponse(SuccessResponse):
    message: str = "Onboarding step completed successfully"
    data: Dict[str, Any]


class OnboardingCompleteResponse(SuccessResponse):
    status_code: int = 201
    message: str = "Onboarding completed successfully! Your AI agents are being set up."
    data: CompanyResponse


# ============================================================================
# BRAND PROFILE SCHEMAS
# ============================================================================

class BrandProfileCreate(BaseModel):
    brand_voice: str
    brand_personality_traits: List[str]
    core_values: List[str]
    unique_value_proposition: str
    content_tone_preferences: Dict[str, int]
    topics_to_avoid: List[str] = Field(default_factory=list)
    preferred_content_formats: List[str]
    content_length_preferences: Dict[str, str] = Field(default_factory=dict)


class BrandProfileResponse(BaseModel):
    id: uuid.UUID
    brand_voice: str
    brand_personality_traits: List[str]
    core_values: List[str]
    unique_value_proposition: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TARGET AUDIENCE SCHEMAS
# ============================================================================

class TargetAudienceCreate(BaseModel):
    name: str
    is_primary: bool = False
    job_titles: List[str]
    industries: List[str]
    company_sizes: List[str]
    pain_points: List[str]
    goals_objectives: List[str]
    preferred_platforms: List[str]


class TargetAudienceResponse(BaseModel):
    id: uuid.UUID
    name: str
    is_primary: bool
    job_titles: List[str]
    industries: List[str]
    pain_points: List[str]
    preferred_platforms: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CONTENT SCHEMAS
# ============================================================================

class ContentBriefCreate(BaseModel):
    title: str
    objective: str
    content_type: str
    target_audience_id: Optional[int] = None
    primary_keyword: Optional[str] = None
    secondary_keywords: List[str] = Field(default_factory=list)
    key_messages: List[str]
    platform_optimizations: Dict[str, Any] = Field(default_factory=dict)


class ContentBriefResponse(BaseModel):
    id: uuid.UUID
    brief_id: uuid.UUID
    title: str
    objective: str
    content_type: str
    status: ContentStatus
    priority_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class ContentBriefListResponse(SuccessResponse):
    message: str = "Content briefs retrieved successfully"
    data: List[ContentBriefResponse]


# ============================================================================
# PLATFORM INTEGRATION SCHEMAS
# ============================================================================

class PlatformIntegrationCreate(BaseModel):
    platform_name: str
    access_token: Optional[str] = None
    additional_credentials: Dict[str, Any] = Field(default_factory=dict)
    platform_settings: Dict[str, Any] = Field(default_factory=dict)


class PlatformIntegrationResponse(BaseModel):
    id: uuid.UUID
    platform_name: str
    is_enabled: bool
    is_connected: bool
    sync_status: str
    last_sync_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PlatformConnectionResponse(SuccessResponse):
    message: str = "Platform connected successfully"
    data: PlatformIntegrationResponse


# ============================================================================
# AGENT & WORKFLOW SCHEMAS
# ============================================================================

class AgentRunCreate(BaseModel):
    agent_type: str
    input_data: Dict[str, Any]
    workflow_run_id: Optional[str] = None


class AgentRunResponse(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    agent_type: str
    status: AgentStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AgentRunStartResponse(SuccessResponse):
    status_code: int = 202
    message: str = "Agent run started successfully"
    data: AgentRunResponse


class WorkflowExecutionRequest(BaseModel):
    company_id: uuid.UUID
    agent_types: List[str] = Field(default=["trend_research", "content_strategy", "brief_generation"])
    config_overrides: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionResponse(SuccessResponse):
    status_code: int = 202
    message: str = "Workflow execution started successfully"
    data: Dict[str, Any]  # Contains workflow_run_id and initial status


# ============================================================================
# ANALYTICS & PERFORMANCE SCHEMAS
# ============================================================================

class PerformanceMetrics(BaseModel):
    impressions: int = 0
    reach: int = 0
    engagement_total: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0


class ContentPerformanceResponse(BaseModel):
    id: uuid.UUID
    platform: str
    content_type: str
    url: Optional[str]
    metrics: PerformanceMetrics
    metrics_date: datetime

    class Config:
        from_attributes = True


class AnalyticsDashboardResponse(SuccessResponse):
    message: str = "Analytics data retrieved successfully"
    data: Dict[str, Any]  # Contains various analytics metrics


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================

class AuthenticationError(ErrorResponse):
    status_code: int = 401
    error_type: str = "authentication_error"
    message: str = "Authentication required"


class AuthorizationError(ErrorResponse):
    status_code: int = 403
    error_type: str = "authorization_error"
    message: str = "Insufficient permissions"


class NotFoundError(ErrorResponse):
    status_code: int = 404
    error_type: str = "not_found"
    message: str = "Resource not found"


class ConflictError(ErrorResponse):
    status_code: int = 409
    error_type: str = "conflict"


class RateLimitError(ErrorResponse):
    status_code: int = 429
    error_type: str = "rate_limit_exceeded"
    message: str = "Too many requests. Please try again later."


class InternalServerError(ErrorResponse):
    status_code: int = 500
    error_type: str = "internal_server_error"
    message: str = "An internal server error occurred"


# ============================================================================
# SPECIFIC ERROR RESPONSES
# ============================================================================

class UserAlreadyExistsError(ConflictError):
    message: str = "A user with this email already exists"
    details: Dict[str, str] = {"field": "email", "code": "already_exists"}


class InvalidCredentialsError(AuthenticationError):
    message: str = "Invalid email or password"


class CompanyNotFoundError(NotFoundError):
    message: str = "Company not found"


class OnboardingNotCompleteError(ErrorResponse):
    status_code: int = 400
    error_type: str = "onboarding_incomplete"
    message: str = "Company onboarding must be completed first"


class PlatformConnectionError(ErrorResponse):
    status_code: int = 400
    error_type: str = "platform_connection_error"
    message: str = "Failed to connect to platform"


class AgentExecutionError(ErrorResponse):
    status_code: int = 500
    error_type: str = "agent_execution_error"
    message: str = "Agent execution failed"


# ============================================================================
# PAGINATION & FILTERING SCHEMAS
# ============================================================================
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")


class PaginatedResponse(SuccessResponse):
    data: List[Any]
    pagination: Dict[str, Any]


class ContentBriefFilters(BaseModel):
    status: Optional[ContentStatus] = None
    content_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None


# ============================================================================
# SUBSCRIPTION & BILLING SCHEMAS
# ============================================================================

class SubscriptionUpdate(BaseModel):
    subscription_tier: SubscriptionTier
    billing_period: str = Field("monthly", pattern="^(monthly|annual)$")


class SubscriptionResponse(BaseModel):
    subscription_tier: SubscriptionTier
    subscription_status: str
    trial_ends_at: Optional[datetime]
    subscription_ends_at: Optional[datetime]
    features: Dict[str, Any]

    class Config:
        from_attributes = True


class BillingInfo(BaseModel):
    current_plan: str
    next_billing_date: Optional[datetime]
    amount_due: float
    payment_method: Optional[str]


# ============================================================================
# SYSTEM CONFIGURATION SCHEMAS
# ============================================================================

class SystemConfigurationUpdate(BaseModel):
    automation_enabled: bool = True
    content_review_required: bool = True
    workflow_frequency: str = Field("weekly", pattern="^(daily|weekly|monthly)$")
    max_briefs_per_run: int = Field(5, ge=1, le=20)
    email_notifications: bool = True


class SystemConfigurationResponse(BaseModel):
    automation_enabled: bool
    content_review_required: bool
    workflow_frequency: str
    email_notifications: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# API RESPONSE HELPERS
# ============================================================================

def create_success_response(
        data: Any = None,
        message: str = "Operation completed successfully",
        status_code: int = 200
) -> SuccessResponse:
    return SuccessResponse(
        success=True,
        message=message,
        status_code=status_code,
        data=data
    )


def create_error_response(
        message: str,
        status_code: int = 400,
        error_type: str = "bad_request",
        details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    return ErrorResponse(
        success=False,
        message=message,
        status_code=status_code,
        error_type=error_type,
        details=details
    )


def create_validation_error_response(
        validation_errors: List[Dict[str, str]]
) -> ValidationErrorResponse:
    return ValidationErrorResponse(
        success=False,
        message="Validation failed",
        status_code=422,
        error_type="validation_error",
        validation_errors=validation_errors
    )


# ============================================================================
# REQUEST/RESPONSE EXAMPLES FOR API DOCUMENTATION
# ============================================================================

class APIExamples:
    USER_CREATE_REQUEST = {
        "email": "john.doe@company.com",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe"
    }

    USER_CREATE_SUCCESS_RESPONSE = {
        "success": True,
        "message": "User created successfully. Please check your email for verification.",
        "status_code": 201,
        "data": {
            "id": 1,
            "email": "john.doe@company.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": True,
            "is_verified": False,
            "created_at": "2024-01-15T10:30:00Z"
        }
    }

    USER_CREATE_ERROR_RESPONSE = {
        "success": False,
        "message": "A user with this email already exists",
        "status_code": 409,
        "error_type": "conflict",
        "details": {
            "field": "email",
            "code": "already_exists"
        }
    }

    ONBOARDING_STEP1_REQUEST = {
        "company_name": "TechStartup Inc",
        "industry": "SaaS",
        "company_size": "11-50",
        "website_url": "https://techstartup.com",
        "description": "AI-powered marketing automation platform"
    }

    ONBOARDING_STEP2_REQUEST = {
        "brand_voice": "Professional but approachable",
        "brand_personality_traits": ["innovative", "reliable", "customer-focused"],
        "core_values": ["transparency", "innovation", "customer success"],
        "unique_value_proposition": "The only marketing platform that combines AI automation with human creativity",
        "content_tone_preferences": {"formal": 40, "casual": 60},
        "topics_to_avoid": ["politics", "controversial topics"],
        "preferred_content_formats": ["blog_posts", "social_posts", "case_studies"]
    }

    WORKFLOW_EXECUTION_REQUEST = {
        "company_id": 1,
        "agent_types": ["trend_research", "content_strategy", "brief_generation"],
        "config_overrides": {
            "max_briefs": 5,
            "focus_keywords": ["marketing automation", "AI tools"]
        }
    }

    WORKFLOW_EXECUTION_RESPONSE = {
        "success": True,
        "message": "Workflow execution started successfully",
        "status_code": 202,
        "data": {
            "workflow_run_id": "wf_run_123456",
            "estimated_completion_time": "2024-01-15T11:00:00Z",
            "agents_queued": ["trend_research", "content_strategy", "brief_generation"]
        }
    }