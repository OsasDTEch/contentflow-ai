import asyncio
import uuid
from schemas.agent_schema import CompanyProfile, TargetAudience
from agents.trend_research_agent import create_trend_research_agent


async def test_agent():
    # Create a simple test profile
    test_audience = TargetAudience(
        name="Tech Professionals",
        pain_points=["Time management", "Staying updated with tech trends"],
        demographics=["25-45 years old", "Software developers", "Tech leads"],
        preferred_platforms=["linkedin", "twitter"],
        content_preferences=["educational content", "industry insights"],
        engagement_patterns=["Morning reading", "Lunch break scrolling"]
    )

    test_profile = CompanyProfile(
        company_id=uuid.uuid4(),
        company_name="TechFlow Solutions",
        industry="Software Development",
        target_audience=test_audience,
        content_themes=["AI trends", "Development tools", "Productivity"],
        competitor_domains=["competitor1.com", "competitor2.com"],
        business_objectives=["Generate leads", "Build thought leadership"],
        brand_voice="Professional and helpful",
        content_preferences=["blog_post", "linkedin_post"],
        posting_frequency_target=5,
        seo_keywords=["software development", "AI tools", "productivity"],
        budget_constraints="Limited budget",
        content_restrictions=["No controversial topics"]
    )

    try:
        print("Creating agent...")
        agent = create_trend_research_agent(test_profile)
        print(f"Agent created: {agent}")

        print("Running agent...")
        query = "Software development trends for tech professionals"
        result = await agent.run(query)

        print(f"Result type: {type(result)}")
        print(f"Result attributes: {dir(result)}")

        if hasattr(result, 'output'):
            print(f"Output type: {type(result.output)}")
            print(f"Output: {result.output}")
        elif hasattr(result, 'data'):
            print(f"Data type: {type(result.data)}")
            print(f"Data: {result.data}")
        else:
            print(f"No output or data attribute found")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent())