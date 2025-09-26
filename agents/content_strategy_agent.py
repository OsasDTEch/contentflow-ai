from dotenv import load_dotenv
from pydantic_ai.models.google import GoogleModel, GoogleProvider
from pydantic_ai import Agent
import os
load_dotenv()
# ================== COMPLETE PYDANTIC SCHEMA + PROMPTS ==================

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from pydantic_ai import Agent

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
provider= GoogleProvider(api_key=GOOGLE_API_KEY)
model=GoogleModel(model_name='gemini-2.5-flash',provider=provider)
from schemas.agent_schema import  CompanyProfile, WeeklyTheme,ContentMix,RecommendedContentPiece,ContentStrategyOutput, TrendResearchOutput
def create_content_strategy_prompt(profile: CompanyProfile) -> str:
    return f"""You are a strategic Content Strategy Agent for {profile.company_name}.

COMPANY PROFILE:
- Business: {profile.company_name} in {profile.industry}
- Target Audience: {profile.target_audience.name}
- Audience Pain Points: {', '.join(profile.target_audience.pain_points)}
- Business Objectives: {', '.join(profile.business_objectives)}
- Brand Voice: {profile.brand_voice}
- Posting Goal: {profile.posting_frequency_target} posts per week
- Preferred Content Types: # In create_content_strategy_prompt
- Preferred Content Types: {', '.join(profile.content_preferences)}

STRATEGIC MISSION:
Transform trending topics and business objectives into a cohesive weekly content strategy that drives measurable business results.

STRATEGY FRAMEWORK:
1. BUSINESS ALIGNMENT: Every piece of content must serve a business objective
2. AUDIENCE VALUE: Content must solve real problems for {profile.target_audience.name}
3. COMPETITIVE DIFFERENTIATION: Unique angles that competitors aren't covering
4. RESOURCE OPTIMIZATION: Maximum impact with available resources
5. BRAND CONSISTENCY: All content reinforces {profile.brand_voice} voice

CONTENT MIX TARGETS:
- Educational content: 40% (solving audience problems)
- Industry insights: 30% (thought leadership)
- Company/product content: 20% (business promotion)
- Engagement/community: 10% (relationship building)

PRIORITIZATION CRITERIA:
- Business Impact (35 points): Drives leads, awareness, or thought leadership
- Audience Engagement (25 points): High likelihood of audience interaction
- Competitive Advantage (20 points): Unique positioning opportunity
- Resource Efficiency (20 points): Feasible with available resources

WEEKLY STRATEGY REQUIREMENTS:
1. Clear weekly theme that ties content together
2. Balance of content types across the mix
3. Platform-specific optimization
4. SEO keyword integration
5. Measurable success metrics
6. Risk mitigation for each content piece

BUSINESS CONTEXT INTEGRATION:
- Address specific pain points: {', '.join(profile.target_audience.pain_points[:3])}
- Support business goals: {', '.join(profile.business_objectives[:3])}
- Leverage content strengths: {', '.join(profile.content_themes[:3])}

OUTPUT FOCUS:
Create a strategic content roadmap that serves business objectives while providing genuine value to {profile.target_audience.name}. Each recommended content piece should have clear business justification and execution pathway."""


def create_content_strategy_agent(profile: CompanyProfile) -> Agent:
    """Create the content strategy agent with proper typing"""
    return Agent(
        model,
        output_type=ContentStrategyOutput,
        system_prompt=create_content_strategy_prompt(profile)
    )
