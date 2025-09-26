# ================== COMPLETE PYDANTIC SCHEMA + PROMPTS ==================
import uuid
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic_ai import Agent
from enum import Enum

# ================== MINIMAL ENUMS (Only where absolutely necessary) ==================

# Keep only the most critical enums for type safety
class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# ================== CORE DATA MODELS ==================

class TargetAudience(BaseModel):
    """Target audience details"""
    name: str = Field(description="Audience segment name")
    pain_points: List[str] = Field(description="Key pain points")
    demographics: List[str] = Field(description="Demographic details")
    preferred_platforms: List[str] = Field(description="Where they spend time")
    content_preferences: List[str] = Field(description="Types of content they prefer")
    engagement_patterns: List[str] = Field(default=[], description="When/how they engage")


class CompanyProfile(BaseModel):
    company_id: uuid.UUID = Field(description="Unique company identifier")
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    target_audience: TargetAudience = Field(description="Target audience details")
    content_themes: List[str] = Field(description="Main content themes")
    competitor_domains: List[str] = Field(description="Competitor websites")
    business_objectives: List[str] = Field(description="Key business goals")
    brand_voice: str = Field(description="Brand voice description")
    content_preferences: List[str] = Field(description="Preferred content types")
    posting_frequency_target: int = Field(ge=1, le=50, description="Posts per week target")
    seo_keywords: List[str] = Field(description="Important SEO keywords")
    budget_constraints: Optional[str] = Field(default=None, description="Budget limitations")
    content_restrictions: List[str] = Field(default=[], description="Content restrictions/guidelines")


# ================== AGENT 1: TREND RESEARCH MODELS ==================

class TrendingTopic(BaseModel):
    """Single trending topic with all relevant data"""
    topic: str = Field(description="The trending topic name")
    trend_score: float = Field(ge=0, le=100, description="Overall relevance score 0-100")
    source: str = Field(description="Where this trend was discovered (google_trends, social_media, news_outlets, etc.)")
    relevance_reason: str = Field(description="Why this trend matters to the company")
    content_angle: str = Field(description="Specific angle to approach this topic")

    # Scoring breakdown
    business_relevance_score: float = Field(ge=0, le=40, description="Business relevance (max 40)")
    audience_interest_score: float = Field(ge=0, le=30, description="Audience interest (max 30)")
    content_opportunity_score: float = Field(ge=0, le=20, description="Content opportunity (max 20)")
    trend_momentum_score: float = Field(ge=0, le=10, description="Trend momentum (max 10)")

    # Recommendations
    recommended_platforms: List[str] = Field(description="Best platforms for this trend")
    target_keywords: List[str] = Field(description="SEO keywords related to this trend")
    competitor_coverage: bool = Field(description="Whether competitors are covering this")
    urgency_level: Literal["high", "medium", "low"] = Field(description="How urgent this trend is")
    trend_lifespan_estimate: str = Field(description="How long this trend will last")


class TrendResearchOutput(BaseModel):
    trending_topics: List[TrendingTopic] = Field(description="List of trending topics found")
    research_summary: str = Field(description="Executive summary of trend research")
    total_topics_found: int = Field(ge=0, description="Total topics analyzed")
    total_topics_qualifying: int = Field(ge=0, description="Topics scoring above 60")
    research_date: str = Field(description="Date when research was conducted")
    research_timeframe: str = Field(default="7d", description="Time period analyzed")
    top_keywords: List[str] = Field(description="Most trending keywords overall")
    industry_insights: List[str] = Field(description="Key industry insights discovered")
    competitive_gaps: List[str] = Field(description="Content gaps vs competitors")
    seasonal_considerations: List[str] = Field(description="Seasonal factors to consider")


# ================== AGENT 2: CONTENT STRATEGY MODELS ==================

class WeeklyTheme(BaseModel):
    """Theme for the week"""
    theme_name: str = Field(description="Name of the weekly theme")
    focus_area: str = Field(description="Main focus area for content")
    key_message: str = Field(description="Core message to communicate")
    target_pain_points: List[str] = Field(description="Audience pain points to address")
    supporting_themes: List[str] = Field(description="Secondary themes to weave in")


class ContentMix(BaseModel):
    """Content type distribution"""
    educational_percentage: float = Field(ge=0, le=100, default=40, description="Educational content %")
    industry_insights_percentage: float = Field(ge=0, le=100, default=30, description="Industry insights %")
    company_product_percentage: float = Field(ge=0, le=100, default=20, description="Company/product content %")
    engagement_community_percentage: float = Field(ge=0, le=100, default=10, description="Engagement content %")

    def validate_total(self) -> bool:
        """Ensure percentages add up to 100"""
        total = (self.educational_percentage + self.industry_insights_percentage +
                 self.company_product_percentage + self.engagement_community_percentage)
        return abs(total - 100) < 0.1


class RecommendedContentPiece(BaseModel):
    """Individual content recommendation"""
    topic: str = Field(description="Content topic")
    priority_score: float = Field(ge=0, le=100, description="Priority score")
    content_type: str = Field(description="Type of content to create (linkedin_post, blog_post, etc.)")
    platform: str = Field(description="Primary platform (linkedin, twitter, etc.)")
    secondary_platforms: List[str] = Field(default=[], description="Additional platforms to consider")

    # Scoring breakdown
    business_impact_score: float = Field(ge=0, le=35, description="Business impact (max 35)")
    audience_engagement_score: float = Field(ge=0, le=25, description="Audience engagement (max 25)")
    competitive_advantage_score: float = Field(ge=0, le=20, description="Competitive advantage (max 20)")
    resource_efficiency_score: float = Field(ge=0, le=20, description="Resource efficiency (max 20)")

    # Execution details
    estimated_effort_hours: float = Field(ge=0, description="Estimated hours to create")
    target_keywords: List[str] = Field(description="SEO keywords for this content")
    related_trends: List[str] = Field(description="Related trending topics")
    success_probability: float = Field(ge=0, le=100, description="Likelihood of success %")


class ContentStrategy(BaseModel):
    """Overall content strategy structure"""
    weekly_theme: WeeklyTheme = Field(description="Theme for the week")
    content_mix: ContentMix = Field(description="Distribution of content types")
    priority_topics: List[str] = Field(description="Top priority topics for the week")
    target_audience_segments: List[str] = Field(description="Specific audience segments to target")
    competitive_differentiation: str = Field(description="How to differentiate from competitors")
    content_calendar_notes: List[str] = Field(description="Important scheduling considerations")


class ContentStrategyOutput(BaseModel):
    content_strategy: ContentStrategy = Field(description="Detailed content strategy")
    recommended_content_pieces: List[RecommendedContentPiece] = Field(description="Specific content recommendations")
    strategy_summary: str = Field(description="Executive summary of the strategy")
    weekly_focus: str = Field(description="Main focus for the week")
    success_metrics: List[str] = Field(description="Key metrics to track")
    risk_mitigation: List[str] = Field(description="Potential risks and mitigation strategies")
    resource_requirements: List[str] = Field(description="Resources needed for execution")
    timeline_considerations: List[str] = Field(description="Important timing factors")


# ================== AGENT 3: BRIEF GENERATION MODELS ==================

class ContentStructure(BaseModel):
    """Structure for the content piece"""
    hook: str = Field(description="Attention-grabbing opening line/paragraph")
    main_points: List[str] = Field(description="3-5 key points to cover in order")
    supporting_details: List[str] = Field(description="Supporting information, stats, examples")
    conclusion: str = Field(description="How to wrap up the content effectively")
    call_to_action: str = Field(description="Specific action for audience to take")
    content_flow: str = Field(description="How the content should flow from start to finish")


class SEOOptimization(BaseModel):
    """SEO optimization details"""
    primary_keyword: str = Field(description="Main keyword to target")
    secondary_keywords: List[str] = Field(description="2-4 additional keywords to include naturally")
    meta_description: str = Field(max_length=160, description="Meta description for SEO")
    title_variations: List[str] = Field(description="3-5 alternative title options")
    target_search_intent: str = Field(description="What search intent this content serves")
    internal_link_opportunities: List[str] = Field(description="Relevant internal pages to link to")
    featured_snippet_optimization: str = Field(description="How to optimize for featured snippets")


class PlatformSpecifications(BaseModel):
    """Platform-specific requirements"""
    optimal_length_words: int = Field(ge=0, description="Optimal word count for platform")
    optimal_length_characters: Optional[int] = Field(ge=0, description="Character count for platforms like Twitter")
    best_posting_time: str = Field(description="Optimal posting time for platform")
    hashtags: List[str] = Field(description="5-10 recommended hashtags")
    visual_requirements: List[str] = Field(description="Visual elements needed (images, videos, etc.)")
    engagement_tactics: List[str] = Field(description="Platform-specific engagement tactics")
    format_specifications: List[str] = Field(description="Platform format requirements")
    cross_promotion_opportunities: List[str] = Field(description="How to promote across other platforms")


class BrandAlignment(BaseModel):
    """Brand alignment specifications"""
    tone: str = Field(description="Tone of voice to use (professional, casual, friendly, etc.)")
    voice_guidelines: List[str] = Field(description="Specific voice guidelines to follow")
    key_messages: List[str] = Field(description="Key brand messages to include")
    brand_values_to_highlight: List[str] = Field(description="Brand values to emphasize")
    messaging_restrictions: List[str] = Field(description="Things to avoid in messaging")
    brand_personality_elements: List[str] = Field(description="Personality traits to showcase")


class SuccessMetrics(BaseModel):
    """Success measurement criteria"""
    primary_kpi: str = Field(description="Main KPI to track (engagement, leads, brand_awareness, etc.)")
    target_engagement_rate: Optional[float] = Field(ge=0, le=100, description="Target engagement rate %")
    target_reach: Optional[int] = Field(ge=0, description="Target reach number")
    target_clicks: Optional[int] = Field(ge=0, description="Target clicks")
    target_leads: Optional[int] = Field(ge=0, description="Target leads generated")
    target_shares: Optional[int] = Field(ge=0, description="Target shares/reposts")
    measurement_timeframe: str = Field(default="7d", description="Time period to measure success")
    benchmark_comparison: str = Field(description="What to compare performance against")


class ExecutionNotes(BaseModel):
    """Execution details"""
    time_estimate_hours: float = Field(ge=0, description="Estimated time to complete")
    difficulty_level: str = Field(description="Complexity level (easy, medium, hard)")
    required_resources: List[str] = Field(description="Resources needed (tools, images, etc.)")
    dependencies: List[str] = Field(description="Any dependencies or prerequisites")
    review_checkpoints: List[str] = Field(description="Key points to review before publishing")
    quality_criteria: List[str] = Field(description="Quality standards to meet")
    potential_challenges: List[str] = Field(description="Potential execution challenges")


class ContentBrief(BaseModel):
    brief_id: str = Field(description="Unique identifier for this brief")
    title: str = Field(description="Working title for the content")
    final_title_options: List[str] = Field(description="3-5 final title options")
    objective: str = Field(description="What this content aims to achieve")
    target_audience_segment: str = Field(description="Specific audience segment")
    content_type: str = Field(description="Type of content (blog_post, linkedin_post, etc.)")
    platform: str = Field(description="Primary platform (linkedin, twitter, etc.)")

    # Detailed specifications
    content_structure: ContentStructure = Field(description="Detailed content structure")
    seo_optimization: SEOOptimization = Field(description="SEO requirements")
    platform_specifications: PlatformSpecifications = Field(description="Platform-specific details")
    brand_alignment: BrandAlignment = Field(description="Brand alignment requirements")
    success_metrics: SuccessMetrics = Field(description="Success measurement")
    execution_notes: ExecutionNotes = Field(description="Execution details")

    # Metadata
    created_date: str = Field(description="When this brief was created")
    priority_level: Literal["high", "medium", "low"] = Field(description="Priority level")
    deadline: Optional[str] = Field(description="Content deadline if any")
    approval_workflow: List[str] = Field(description="Who needs to approve this content")


class BriefGenerationOutput(BaseModel):
    content_briefs: List[ContentBrief] = Field(description="Generated content briefs")
    total_briefs_generated: int = Field(ge=0, description="Number of briefs created")
    generation_date: str = Field(description="When briefs were generated")
    strategy_alignment_score: float = Field(ge=0, le=100, description="How well briefs align with strategy")
    estimated_total_hours: float = Field(ge=0, description="Total estimated execution time")
    resource_summary: List[str] = Field(description="Summary of all resources needed")
    timeline_overview: str = Field(description="Suggested execution timeline")