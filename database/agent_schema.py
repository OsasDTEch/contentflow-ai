from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# AGENT STATUS ENUMS
# ============================================================================

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class TrendUrgency(str, Enum):
    TRENDING_NOW = "trending_now"
    GROWING = "growing"
    STABLE = "stable"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    LINKEDIN_POST = "linkedin_post"
    TWITTER_THREAD = "twitter_thread"
    SOCIAL_POST = "social_post"
    EMAIL_NEWSLETTER = "email_newsletter"


# ============================================================================
# TREND RESEARCH AGENT SCHEMAS
# ============================================================================

class TrendResearchInput(BaseModel):
    company_id: str
    industry: str
    target_audience: Dict[str, Any] = Field(..., description="Target audience details from onboarding")
    content_themes: List[str] = Field(..., description="Content themes from onboarding")
    competitor_domains: List[str] = Field(default_factory=list)
    research_timeframe: str = Field(default="7d")
    focus_keywords: List[str] = Field(default_factory=list)


class TrendingTopic(BaseModel):
    topic: str
    trend_score: float = Field(..., ge=0, le=100, description="Relevance score 0-100")
    source: str
    relevance_reason: str
    content_angle: str
    search_volume_estimate: str = Field(..., regex="^(Low|Medium|High)$")
    competition_level: str = Field(..., regex="^(Low|Medium|High)$")
    recommended_platforms: List[str]
    keywords: List[str] = Field(default_factory=list)
    urgency: TrendUrgency


class TrendResearchOutput(BaseModel):
    trending_topics: List[TrendingTopic]
    research_summary: str
    total_topics_found: int
    research_date: datetime
    next_research_scheduled: datetime


# ============================================================================
# CONTENT STRATEGY AGENT SCHEMAS
# ============================================================================

class ContentStrategyInput(BaseModel):
    trending_topics: List[TrendingTopic]
    company_profile: Dict[str, Any]
    target_audience: Dict[str, Any]
    business_objectives: List[str]
    content_preferences: Dict[str, Any]
    content_calendar: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: Optional[Dict[str, Any]] = None


class ContentMix(BaseModel):
    educational: int = Field(..., ge=0, le=100)
    industry_insights: int = Field(..., ge=0, le=100)
    company_content: int = Field(..., ge=0, le=100)
    engagement_content: int = Field(..., ge=0, le=100)


class ContentStrategy(BaseModel):
    weekly_theme: str
    content_pillars: List[str]
    content_mix: ContentMix


class PriorityContentPiece(BaseModel):
    topic: str
    priority_score: float = Field(..., ge=0, le=100)
    content_type: ContentType
    target_platform: str
    business_objective: str
    target_audience_segment: str
    strategic_reasoning: str
    expected_outcome: str
    content_pillar: str
    urgency: str = Field(..., regex="^(This Week|Next Week|This Month)$")
    difficulty_level: DifficultyLevel
    estimated_engagement: str


class ContentStrategyOutput(BaseModel):
    content_strategy: ContentStrategy
    priority_content_pieces: List[PriorityContentPiece]
    strategy_rationale: str
    weekly_focus: str
    content_gaps: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)


# ============================================================================
# BRIEF GENERATION AGENT SCHEMAS
# ============================================================================

class BriefGenerationInput(BaseModel):
    selected_topic: PriorityContentPiece
    company_profile: Dict[str, Any]
    target_audience: Dict[str, Any]
    content_specifications: Dict[str, Any]
    seo_keywords: Dict[str, List[str]]
    business_context: Dict[str, Any]


class Hook(BaseModel):
    opening_line: str
    problem_statement: str
    value_promise: str


class ContentSection(BaseModel):
    section_title: str
    key_points: List[str]
    supporting_details: List[str]
    examples: List[str] = Field(default_factory=list)
    data_points: List[str] = Field(default_factory=list)


class Conclusion(BaseModel):
    key_takeaway: str
    next_steps: List[str]
    call_to_action: str


class ContentStructure(BaseModel):
    hook: Hook
    main_content: List[ContentSection]
    conclusion: Conclusion


class SEOOptimization(BaseModel):
    meta_title: str = Field(..., max_length=60)
    meta_description: str = Field(..., max_length=160)
    primary_keyword: str
    secondary_keywords: List[str]
    keyword_placement: Dict[str, str] = Field(default_factory=dict)
    internal_link_opportunities: List[str] = Field(default_factory=list)


class PlatformSpecifications(BaseModel):
    optimal_length: str
    best_posting_time: str
    hashtag_recommendations: List[str] = Field(default_factory=list)
    visual_suggestions: str
    engagement_tactics: List[str]
    cross_platform_adaptations: Dict[str, str] = Field(default_factory=dict)


class BrandAlignment(BaseModel):
    tone_guidelines: str
    voice_examples: List[str]
    key_messages_to_include: List[str]
    messaging_to_avoid: List[str]
    brand_story_connection: str


class ContentBrief(BaseModel):
    brief_id: str
    title: str
    subtitle: Optional[str] = None
    objective: str
    target_audience: str
    content_type: ContentType
    target_platform: str
    content_structure: ContentStructure
    seo_optimization: SEOOptimization
    platform_specifications: PlatformSpecifications
    brand_alignment: BrandAlignment


class ExecutionGuide(BaseModel):
    difficulty_level: DifficultyLevel
    estimated_time: str
    required_resources: List[str]
    research_requirements: List[str] = Field(default_factory=list)
    approval_requirements: str


class SuccessMeasurement(BaseModel):
    primary_kpi: str
    target_metrics: Dict[str, str]
    tracking_instructions: str
    optimization_opportunities: List[str]


class CompetitiveContext(BaseModel):
    differentiation_points: List[str]
    market_gap_addressed: str
    competitive_advantages: List[str]


class BriefGenerationOutput(BaseModel):
    content_brief: ContentBrief
    execution_guide: ExecutionGuide
    success_measurement: SuccessMeasurement
    competitive_context: CompetitiveContext


# ============================================================================
# AGENT EXECUTION TRACKING SCHEMAS
# ============================================================================

class AgentExecutionRequest(BaseModel):
    agent_type: str = Field(..., regex="^(trend_research|content_strategy|brief_generation)$")
    company_id: str
    input_data: Dict[str, Any]
    workflow_run_id: Optional[str] = None


class AgentExecutionResponse(BaseModel):
    success: bool
    agent_type: str
    execution_id: str
    status: AgentStatus
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowExecutionRequest(BaseModel):
    company_id: str
    agents_to_run: List[str] = Field(default=["trend_research", "content_strategy", "brief_generation"])
    config_overrides: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionResponse(BaseModel):
    success: bool
    workflow_run_id: str
    status: str
    agents_completed: List[str] = Field(default_factory=list)
    agents_failed: List[str] = Field(default_factory=list)
    total_briefs_generated: int
    execution_summary: str
    started_at: datetime
    estimated_completion: Optional[datetime] = None


# ============================================================================
# API RESPONSE WRAPPERS
# ============================================================================

class AgentSuccessResponse(BaseModel):
    success: bool = True
    message: str
    status_code: int = 200
    data: AgentExecutionResponse


class AgentErrorResponse(BaseModel):
    success: bool = False
    message: str
    status_code: int = 500
    error_type: str = "agent_execution_error"
    details: Optional[Dict[str, Any]] = None


class WorkflowSuccessResponse(BaseModel):
    success: bool = True
    message: str = "Workflow execution completed successfully"
    status_code: int = 200
    data: WorkflowExecutionResponse


# ============================================================================
# SIMPLIFIED AGENT SCHEMAS (For Your MVP)
# ============================================================================

class SimpleTrendInput(BaseModel):
    """Simplified input for MVP trend research"""
    industry: str
    target_audience_name: str
    pain_points: List[str]
    content_themes: List[str]


class SimpleTrend(BaseModel):
    """Simple trend output for MVP"""
    topic: str
    score: float
    source: str
    why_relevant: str
    content_idea: str


class SimpleTrendOutput(BaseModel):
    trends: List[SimpleTrend]
    summary: str


class SimpleStrategyInput(BaseModel):
    """Simplified strategy input for MVP"""
    trends: List[SimpleTrend]
    company_name: str
    brand_voice: str
    business_goals: List[str]


class SimpleContentIdea(BaseModel):
    topic: str
    priority: int = Field(..., ge=1, le=10)
    content_type: str
    platform: str
    why_create: str


class SimpleStrategyOutput(BaseModel):
    content_ideas: List[SimpleContentIdea]
    weekly_theme: str


class SimpleBriefInput(BaseModel):
    """Simplified brief input for MVP"""
    content_idea: SimpleContentIdea
    company_name: str
    target_audience: str
    brand_voice: str


class SimpleBrief(BaseModel):
    """Simple brief for MVP customers"""
    title: str
    hook: str
    main_points: List[str]
    call_to_action: str
    hashtags: List[str]
    best_time_to_post: str
    why_this_works: str


class SimpleBriefOutput(BaseModel):
    brief: SimpleBrief
    estimated_engagement: str


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_usage():
    """Example of how to use these schemas"""

    # Trend Research Input
    trend_input = TrendResearchInput(
        company_id="comp_123",
        industry="SaaS",
        target_audience={
            "name": "Marketing Managers",
            "pain_points": ["Too much manual work", "Hard to prove ROI"]
        },
        content_themes=["marketing automation", "productivity tools"],
        focus_keywords=["marketing automation", "saas tools"]
    )

    # Simple MVP Version
    simple_trend_input = SimpleTrendInput(
        industry="SaaS",
        target_audience_name="Marketing Managers",
        pain_points=["Too much manual work"],
        content_themes=["marketing automation"]
    )

    return trend_input, simple_trend_input

# For your agents, use the Simple* schemas for MVP
# Use the full schemas when you add advanced features later