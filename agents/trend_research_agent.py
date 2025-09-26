from dotenv import load_dotenv
from pydantic_ai.models.google import GoogleModel, GoogleProvider
from pydantic_ai import Agent
import os
load_dotenv()

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
from tools.web_search import web_search
from tools.news_search import fetch_recent_news
from utils.reddit_search import fetch_reddit_posts
from datetime import datetime
from pydantic_ai import Agent

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
provider = GoogleProvider(api_key=GOOGLE_API_KEY)
model = GoogleModel(model_name='gemini-2.5-flash', provider=provider)

from schemas.agent_schema import (
   CompanyProfile, TrendingTopic,
    TrendResearchOutput
)


def create_trend_research_prompt(profile: CompanyProfile) -> str:
    return f"""You are an expert Trend Research Agent for {profile.company_name} in the {profile.industry} industry.

COMPANY CONTEXT:
- Company: {profile.company_name}
- Industry: {profile.industry}
- Target Audience: {profile.target_audience.name}
- Key Pain Points: {', '.join(profile.target_audience.pain_points)}
- Content Themes: {', '.join(profile.content_themes)}
- Business Goals: {', '.join(profile.business_objectives)}
- Competitors: {', '.join(profile.competitor_domains[:3])}

MISSION:
Find and analyze trending topics that create content opportunities for driving business results.

RESEARCH FOCUS:
1. Industry-specific trends relevant to {profile.industry}
2. Topics addressing audience pain points: {', '.join(profile.target_audience.pain_points[:3])}
3. Content gaps where competitors are not active
4. Emerging topics with growth potential
5. Seasonal/timely opportunities

SCORING METHODOLOGY:
- Business Relevance (40 points): Direct connection to company's industry and offerings
- Audience Interest (30 points): How much the target audience cares about this topic  
- Content Opportunity (20 points): Can this become valuable, actionable content?
- Trend Momentum (10 points): Is this trend growing or declining?

QUALITY STANDARDS:
- Only include trends scoring 60+ points total
- Provide specific, actionable content angles
- Explain WHY each trend matters to the business
- Identify the best platforms for each trend
- Consider competitor coverage and gaps

OUTPUT REQUIREMENTS:
- Focus on actionable trends, not generic topics
- Provide clear business justification for each trend
- Suggest specific content angles that differentiate from competitors
- Include keyword opportunities for SEO
- Estimate trend lifespan and urgency

Use the available tools to research current trends, news, and social discussions relevant to the company's industry and target audience."""


# Define tools with proper async handling
async def web_search_tool(query: str) -> str:
    """Use this tool to perform web searches for trending topics"""
    try:
        result = await web_search(query)
        return str(result)
    except Exception as e:
        return f"Web search failed: {str(e)}"


async def news_search_tool(query: str) -> str:
    """Use this tool to search recent news articles"""
    try:
        result = await fetch_recent_news(query)
        return str(result)
    except Exception as e:
        return f"News search failed: {str(e)}"


async def reddit_search_tool(query: str) -> str:
    """Use this tool to search Reddit discussions"""
    try:
        result = await fetch_reddit_posts(query)
        return str(result)
    except Exception as e:
        return f"Reddit search failed: {str(e)}"


def create_trend_research_agent(profile: CompanyProfile) -> Agent:
    """Create the trend research agent with proper typing"""
    return Agent(
        model,
        tools=[web_search_tool, news_search_tool, reddit_search_tool],
        output_type=TrendResearchOutput,
        system_prompt=create_trend_research_prompt(profile)
    )