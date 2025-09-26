from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from typing import Optional
from database.db import Base


# Enums
class SubscriptionTier(str, enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class CompanySize(str, enum.Enum):
    STARTUP = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1000+"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# ============================================================================
# USER & AUTHENTICATION MODELS
# ============================================================================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company_memberships = relationship(
        "CompanyMember",
        back_populates="user",
        foreign_keys="CompanyMember.user_id"  # 👈 only via user_id
    )
    created_companies = relationship(
        "Company",
        back_populates="creator",
        foreign_keys="Company.creator_id"
    )
    invited_members = relationship(
        "CompanyMember",
        back_populates="inviter",
        foreign_keys="CompanyMember.invited_by"  # 👈 only via invited_by
    )

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True, index=True)  # company website domain
    industry = Column(String(100), nullable=False)
    company_size = Column(Enum(CompanySize), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)

    # Subscription info
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.STARTER)
    subscription_status = Column(String(50), default="trial")  # trial, active, cancelled, past_due
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_starts_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)

    # Onboarding status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=1)  # Current step in onboarding

    # Metadata
    creator_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Add to Company model:
    settings = Column(JSON, nullable=True)  # Store various settings
    onboarding_completed_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("User", back_populates="created_companies")
    members = relationship("CompanyMember", back_populates="company")
    brand_profile = relationship("BrandProfile", back_populates="company", uselist=False)
    target_audiences = relationship("TargetAudience", back_populates="company")
    content_themes = relationship("ContentTheme", back_populates="company")
    competitors = relationship("Competitor", back_populates="company")
    platform_integrations = relationship("PlatformIntegration", back_populates="company")
    content_briefs = relationship("ContentBrief", back_populates="company")
    agent_runs = relationship("AgentRun", back_populates="company")
    workflow_runs = relationship("WorkflowRun", back_populates="company")


class CompanyMember(Base):
    __tablename__ = "company_members"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    is_active = Column(Boolean, default=True)
    invited_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship(
        "User",
        back_populates="company_memberships",
        foreign_keys=[user_id]
    )
    inviter = relationship(
        "User",
        back_populates="invited_members",
        foreign_keys=[invited_by]
    )
    company = relationship("Company", back_populates="members")
# ============================================================================
# COMPANY PROFILE & ONBOARDING MODELS
# ============================================================================

class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False, unique=True)

    # Brand Voice & Personality
    brand_voice = Column(String(100), nullable=True)  # Professional, Casual, Authoritative, Friendly
    brand_personality_traits = Column(JSON, nullable=True)  # ["innovative", "reliable", "approachable"]
    core_values = Column(JSON, nullable=True)  # ["transparency", "customer-first", "innovation"]
    unique_value_proposition = Column(Text, nullable=True)

    # Content Guidelines
    content_tone_preferences = Column(JSON, nullable=True)  # {"formal": 30, "casual": 70}
    topics_to_avoid = Column(JSON, nullable=True)  # ["politics", "religion"]
    preferred_content_formats = Column(JSON, nullable=True)  # ["blog_posts", "social_posts", "videos"]
    content_length_preferences = Column(JSON, nullable=True)  # {"blog": "1500-2500", "social": "100-200"}
    visual_style_preferences = Column(JSON, nullable=True)
    compliance_requirements = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="brand_profile")


class TargetAudience(Base):
    __tablename__ = "target_audiences"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    # Audience Details
    name = Column(String(255), nullable=False)  # "Marketing Managers"
    is_primary = Column(Boolean, default=False)
    job_titles = Column(JSON, nullable=True)  # ["Marketing Manager", "VP Marketing"]
    industries = Column(JSON, nullable=True)  # ["SaaS", "E-commerce"]
    company_sizes = Column(JSON, nullable=True)  # ["51-200", "201-1000"]
    geographic_locations = Column(JSON, nullable=True)  # ["United States", "Canada"]
    age_demographics = Column(String(50), nullable=True)  # "25-45"

    # Pain Points & Goals
    pain_points = Column(JSON, nullable=True)  # ["lead qualification", "attribution"]
    goals_objectives = Column(JSON, nullable=True)  # ["increase leads", "improve ROI"]
    professional_challenges = Column(JSON, nullable=True)

    # Behavior & Preferences
    preferred_platforms = Column(JSON, nullable=True)  # ["linkedin", "twitter"]
    content_consumption_behavior = Column(JSON, nullable=True)
    engagement_triggers = Column(JSON, nullable=True)
    optimal_posting_times = Column(JSON, nullable=True)  # {"linkedin": ["9:00", "12:00"]}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="target_audiences")


class ContentTheme(Base):
    __tablename__ = "content_themes"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    name = Column(String(255), nullable=False)  # "Marketing Automation"
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # ["automation", "workflows", "efficiency"]
    priority_score = Column(Integer, default=50)  # 1-100
    is_evergreen = Column(Boolean, default=True)  # vs trending content
    seasonal_relevance = Column(JSON, nullable=True)  # {"months": [1,2,3], "events": ["Black Friday"]}

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="content_themes")


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    competitive_advantages = Column(JSON, nullable=True)  # What makes us better
    social_profiles = Column(JSON, nullable=True)  # {"linkedin": "url", "twitter": "url"}
    content_analysis_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="competitors")


# ============================================================================
# PLATFORM INTEGRATION MODELS
# ============================================================================

class PlatformIntegration(Base):
    __tablename__ = "platform_integrations"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    platform_name = Column(String(100), nullable=False)  # "linkedin", "twitter", "wordpress"
    is_enabled = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)

    # Encrypted credentials/tokens
    access_token = Column(Text, nullable=True)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    additional_credentials = Column(JSON, nullable=True)  # Platform-specific data

    # Platform-specific settings
    platform_settings = Column(JSON, nullable=True)  # Publishing preferences, etc.
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="pending")  # pending, success, error

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="platform_integrations")


# ============================================================================
# CONTENT & WORKFLOW MODELS
# ============================================================================

class ContentBrief(Base):
    __tablename__ = "content_briefs"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    # Brief Details
    title = Column(String(500), nullable=False)
    objective = Column(Text, nullable=False)
    content_type = Column(String(100), nullable=False)  # "blog_post", "social_post", "video"
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)

    # Target & Strategy
    target_audience_id = Column(UUID, ForeignKey("target_audiences.id"), nullable=True)
    content_theme_id = Column(UUID, ForeignKey("content_themes.id"), nullable=True)
    key_messages = Column(JSON, nullable=True)
    content_outline = Column(JSON, nullable=True)

    # SEO & Optimization
    primary_keyword = Column(String(255), nullable=True)
    secondary_keywords = Column(JSON, nullable=True)
    meta_description = Column(String(500), nullable=True)

    # Platform Adaptations
    platform_optimizations = Column(JSON, nullable=True)  # Platform-specific versions
    hashtags = Column(JSON, nullable=True)
    call_to_action = Column(String(500), nullable=True)

    # Creative Direction
    tone_voice = Column(String(100), nullable=True)
    visual_style = Column(String(100), nullable=True)

    # Scheduling
    scheduled_publish_date = Column(DateTime, nullable=True)
    priority_score = Column(Float, default=50.0)

    # Performance Tracking
    performance_metrics = Column(JSON, nullable=True)
    feedback = Column(JSON, nullable=True)

    # Metadata
    brief_id = Column(String(100), unique=True, nullable=False)  # Human-readable ID
    created_by_agent = Column(String(100), nullable=True)  # Which agent created this
    agent_run_id = Column(UUID, ForeignKey("agent_runs.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="content_briefs")
    agent_run = relationship("AgentRun", back_populates="content_briefs")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    # Run Details
    run_id = Column(String(100), unique=True, nullable=False)
    agent_type = Column(String(100), nullable=False)  # "trend_research", "content_strategy"
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)

    # Input/Output
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Workflow Context
    workflow_run_id = Column(String(100), nullable=True)  # Groups related agent runs
    parent_agent_run_id = Column(UUID, ForeignKey("agent_runs.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="agent_runs")
    content_briefs = relationship("ContentBrief", back_populates="agent_run")
    child_runs = relationship("AgentRun", backref="parent_run", remote_side=[id])


class ContentCalendar(Base):
    __tablename__ = "content_calendars"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)
    content_brief_id = Column(UUID, ForeignKey("content_briefs.id"), nullable=False)

    # Scheduling
    scheduled_date = Column(DateTime, nullable=False)
    platform = Column(String(100), nullable=False)
    posting_time = Column(String(10), nullable=True)  # "09:00"
    timezone = Column(String(50), default="UTC")

    # Status
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)

    # Platform-specific data
    platform_post_id = Column(String(255), nullable=True)  # ID on the platform
    platform_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# ANALYTICS & PERFORMANCE MODELS
# ============================================================================

class ContentPerformance(Base):
    __tablename__ = "content_performance"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)
    content_brief_id = Column(UUID, ForeignKey("content_briefs.id"), nullable=True)

    # Platform & Content Info
    platform = Column(String(100), nullable=False)
    content_type = Column(String(100), nullable=False)
    platform_post_id = Column(String(255), nullable=True)
    url = Column(String(500), nullable=True)

    # Performance Metrics
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_total = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    saves = Column(Integer, default=0)

    # Calculated Metrics
    engagement_rate = Column(Float, default=0.0)
    click_through_rate = Column(Float, default=0.0)

    # Time-based tracking
    metrics_date = Column(DateTime, nullable=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # Raw data from platforms
    raw_metrics = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# SYSTEM & CONFIGURATION MODELS
# ============================================================================

class SystemConfiguration(Base):
    __tablename__ = "system_configurations"

    id = Column(UUID, primary_key=True, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    # AI Agent Settings
    agent_settings = Column(JSON, nullable=True)
    automation_enabled = Column(Boolean, default=True)
    content_review_required = Column(Boolean, default=True)

    # Workflow Settings
    workflow_frequency = Column(String(50), default="weekly")  # daily, weekly, monthly
    max_briefs_per_run = Column(Integer, default=5)

    # Notification Settings
    email_notifications = Column(Boolean, default=True)
    slack_webhook_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add these models to your existing models.py file

    # ============================================================================
    # WORKFLOW OUTPUT MODELS - Add after existing models
    # ============================================================================


# Add these models to your existing models.py file

# ============================================================================
# WORKFLOW OUTPUT MODELS - Add after existing models
# ============================================================================

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Run metadata
    workflow_id = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="running")  # running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Results summary
    trends_found = Column(Integer, default=0)
    strategy_created = Column(Boolean, default=False)
    briefs_generated = Column(Integer, default=0)

    # Error tracking
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company")
    trending_topics = relationship("TrendingTopicResult", back_populates="workflow_run")
    content_strategies = relationship("ContentStrategyResult", back_populates="workflow_run")
    content_brief_results = relationship("ContentBriefResult", back_populates="workflow_run")


class TrendingTopicResult(Base):
    __tablename__ = "trending_topic_results"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Core trend data
    topic = Column(String(500), nullable=False)
    trend_score = Column(Float, default=0.0)
    source = Column(String(100), nullable=True)
    relevance_reason = Column(Text, nullable=True)
    content_angle = Column(Text, nullable=True)

    # Scoring breakdown
    business_relevance_score = Column(Float, default=0.0)
    audience_interest_score = Column(Float, default=0.0)
    content_opportunity_score = Column(Float, default=0.0)
    trend_momentum_score = Column(Float, default=0.0)

    # Recommendations
    recommended_platforms = Column(JSON, nullable=True)  # ["linkedin", "twitter"]
    target_keywords = Column(JSON, nullable=True)
    competitor_coverage = Column(Boolean, default=False)
    urgency_level = Column(String(20), default="medium")
    trend_lifespan_estimate = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="trending_topics")
    company = relationship("Company")


class ContentStrategyResult(Base):
    __tablename__ = "content_strategy_results"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Strategy overview
    strategy_summary = Column(Text, nullable=True)
    weekly_focus = Column(String(500), nullable=True)

    # Weekly theme data
    theme_name = Column(String(255), nullable=True)
    focus_area = Column(String(500), nullable=True)
    key_message = Column(Text, nullable=True)
    target_pain_points = Column(JSON, nullable=True)
    supporting_themes = Column(JSON, nullable=True)

    # Content mix percentages
    educational_percentage = Column(Float, default=40.0)
    industry_insights_percentage = Column(Float, default=30.0)
    company_product_percentage = Column(Float, default=20.0)
    engagement_community_percentage = Column(Float, default=10.0)

    # Strategy details
    priority_topics = Column(JSON, nullable=True)
    target_audience_segments = Column(JSON, nullable=True)
    competitive_differentiation = Column(Text, nullable=True)
    content_calendar_notes = Column(JSON, nullable=True)

    # Metrics and requirements
    success_metrics = Column(JSON, nullable=True)
    risk_mitigation = Column(JSON, nullable=True)
    resource_requirements = Column(JSON, nullable=True)
    timeline_considerations = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="content_strategies")
    company = relationship("Company")
    recommended_content_pieces = relationship("RecommendedContentPiece", back_populates="strategy_result")


class RecommendedContentPiece(Base):
    __tablename__ = "recommended_content_pieces"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    strategy_result_id = Column(UUID(as_uuid=True), ForeignKey("content_strategy_results.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Content details
    topic = Column(String(500), nullable=False)
    priority_score = Column(Float, default=0.0)
    content_type = Column(String(100), nullable=True)
    platform = Column(String(50), nullable=True)
    secondary_platforms = Column(JSON, nullable=True)

    # Scoring breakdown
    business_impact_score = Column(Float, default=0.0)
    audience_engagement_score = Column(Float, default=0.0)
    competitive_advantage_score = Column(Float, default=0.0)
    resource_efficiency_score = Column(Float, default=0.0)

    # Execution details
    estimated_effort_hours = Column(Float, default=0.0)
    target_keywords = Column(JSON, nullable=True)
    related_trends = Column(JSON, nullable=True)
    success_probability = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    strategy_result = relationship("ContentStrategyResult", back_populates="recommended_content_pieces")
    company = relationship("Company")


class ContentBriefResult(Base):
    __tablename__ = "content_brief_results"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Brief identification
    brief_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    final_title_options = Column(JSON, nullable=True)
    objective = Column(Text, nullable=True)
    target_audience_segment = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=True)
    platform = Column(String(50), nullable=True)

    # Content structure - stored as JSON for flexibility
    content_structure = Column(JSON, nullable=True)  # hook, main_points, etc.
    seo_optimization = Column(JSON, nullable=True)  # keywords, meta_description, etc.
    platform_specifications = Column(JSON, nullable=True)  # length, hashtags, etc.
    brand_alignment = Column(JSON, nullable=True)  # tone, voice_guidelines, etc.
    success_metrics = Column(JSON, nullable=True)  # KPIs, targets, etc.
    execution_notes = Column(JSON, nullable=True)  # time_estimate, resources, etc.

    # Metadata
    priority_level = Column(String(20), default="medium")
    deadline = Column(DateTime, nullable=True)
    approval_workflow = Column(JSON, nullable=True)

    # Generation metadata
    strategy_alignment_score = Column(Float, default=0.0)
    generation_date = Column(DateTime(timezone=True), server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="content_brief_results")
    company = relationship("Company")




