import asyncio
from workflow.initial_graph import content_graph, ContentWorkflowState
from schemas.agent_schema import CompanyProfile, TargetAudience

async def test_workflow():
    fake_profile = CompanyProfile(
        company_id="123",
        company_name="TestCo",
        industry="AI",
        target_audience=TargetAudience(
            name="Developers",
            pain_points=["scaling AI apps"],
            demographics=["25-40 engineers"],
            preferred_platforms=["linkedin", "twitter"],
            content_preferences=["blog_post", "linkedin_post"],
            engagement_patterns=["weekdays morning"]
        ),
        content_themes=["AI trends", "Automation"],
        competitor_domains=["openai.com", "anthropic.com"],
        business_objectives=["thought_leadership", "engagement"],
        brand_voice="professional but approachable",
        content_preferences=["blog_post", "twitter_post"],
        posting_frequency_target=3,
        seo_keywords=["AI automation", "LLM workflows"],
        budget_constraints=None,
        content_restrictions=[],
    )

    init_state: ContentWorkflowState = {
        "company_id": fake_profile.company_id,
        "profile": fake_profile,
        "trends": None,
        "strategy": None,
        "briefs": [],
        "error": None,
        "current_step": "start",
    }

    result = await content_graph.ainvoke(init_state)
    print(result)

if __name__ == "__main__":
    asyncio.run(test_workflow())
