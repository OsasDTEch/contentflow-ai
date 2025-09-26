from typing import Optional, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from datetime import datetime

# Import your agents and outputs
from agents.brief_generation_agent import (
    create_brief_generation_agent,
    BriefGenerationOutput,
)
from agents.content_strategy_agent import (
    create_content_strategy_agent,
    ContentStrategyOutput,
)
from agents.trend_research_agent import (
    create_trend_research_agent,
    TrendResearchOutput,
)
from schemas.agent_schema import CompanyProfile


# ================== STATE DEFINITION ==================
class ContentWorkflowState(TypedDict):
    company_id: str
    profile: CompanyProfile
    trends: Optional[TrendResearchOutput]
    strategy: Optional[ContentStrategyOutput]
    briefs: Optional[BriefGenerationOutput]
    error: Optional[str]
    current_step: str


# ================== NODES ==================
async def trend_research_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Research trending topics relevant to the company"""
    try:
        print(f"Starting trend research for {state['profile'].company_name}")
        company_info = state["profile"]
        agent = create_trend_research_agent(company_info)

        # Create research query based on company profile
        research_query = f"{company_info.industry} trends for {company_info.target_audience.name}"
        print(f"Research query: {research_query}")

        # Run agent with query
        print("Running agent...")
        agent_result = await agent.run(research_query)
        print(f"Agent result type: {type(agent_result)}")
        # print(f"Agent result attributes: {dir(agent_result)}")

        # Extract the actual data from AgentRunResult
        # The agent_result.output contains the TrendResearchOutput
        trends_data = agent_result.output
        print(f"{trends_data}")

        # Validate it's the right type
        if not isinstance(trends_data, TrendResearchOutput):
            print(f"ERROR: Expected TrendResearchOutput, got {type(trends_data)}")
            print(f"Data content: {trends_data}")
            raise ValueError(f"Expected TrendResearchOutput, got {type(trends_data)}")

        state["trends"] = trends_data
        state["current_step"] = "trend_research_done"
        print(f"Trend research completed: {len(trends_data.trending_topics)} topics found")

    except Exception as e:
        print(f"Trend Research Error: {str(e)}")
        import traceback
        traceback.print_exc()
        state["error"] = f"Trend Research Failed: {str(e)}"

    return state


async def content_strategy_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Create content strategy based on trends and company profile"""
    try:
        print(f"Starting content strategy for {state['profile'].company_name}")
        company_info = state["profile"]
        trends = state["trends"]

        print(f"Company info content_preferences type: {type(company_info.content_preferences)}")
        print(f"Company info content_preferences: {company_info.content_preferences}")

        agent = create_content_strategy_agent(company_info)

        # Create strategy input combining profile and trends
        strategy_input = f"""
        Company: {company_info.company_name}
        Industry: {company_info.industry}
        Business Objectives: {', '.join(company_info.business_objectives)}

        Available Trends:
        {', '.join([topic.topic for topic in trends.trending_topics]) if trends and trends.trending_topics else 'No specific trends found'}

        Create a weekly content strategy addressing audience pain points: {', '.join(company_info.target_audience.pain_points)}
        """

        print("Running content strategy agent...")
        agent_result = await agent.run(strategy_input)
        print(f"Strategy result type: {type(agent_result)}")
        print(f"Strategy result attributes: {dir(agent_result)}")

        # Extract the actual data from AgentRunResult
        strategy_data = agent_result.output
        # print(f"Strategy data type: {type(strategy_data)}")

        # Validate it's the right type
        if not isinstance(strategy_data, ContentStrategyOutput):
            print(f"ERROR: Expected ContentStrategyOutput, got {type(strategy_data)}")
            print(f"Data content: {strategy_data}")
            raise ValueError(f"Expected ContentStrategyOutput, got {type(strategy_data)}")

        state["strategy"] = strategy_data
        state["current_step"] = "content_strategy_done"
        print("Content strategy completed")

    except Exception as e:
        print(f"Content Strategy Error: {str(e)}")
        import traceback
        traceback.print_exc()
        state["error"] = f"Content Strategy Failed: {str(e)}"

    return state




def truncate_meta_descriptions(output: BriefGenerationOutput) -> BriefGenerationOutput:
    """
    Ensure all meta_descriptions are <= 160 characters.
    """
    if hasattr(output, "content_briefs"):
        for brief in output.content_briefs:
            if hasattr(brief, "seo_optimization") and brief.seo_optimization:
                if len(brief.seo_optimization.meta_description) > 160:
                    brief.seo_optimization.meta_description = (
                        brief.seo_optimization.meta_description[:157] + "..."
                    )
    return output


async def brief_generation_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Generate detailed content briefs based on strategy"""
    try:
        company_info = state["profile"]
        strategy = state.get("strategy")
        trends = state.get("trends")

        print(f"Starting brief generation for {company_info.company_name}")
        agent = create_brief_generation_agent(company_info)

        # Build input
        brief_input = f"""
        Company: {company_info.company_name}
        Target Audience: {company_info.target_audience.name}
        Brand Voice: {company_info.brand_voice}

        Strategy Focus: {strategy.weekly_focus if strategy else 'General content strategy'}

        Available Topics:
        {', '.join([piece.topic for piece in strategy.recommended_content_pieces]) if strategy and strategy.recommended_content_pieces else 'General content topics'}

        Trending Keywords:
        {', '.join(trends.top_keywords[:5]) if trends and trends.top_keywords else 'General industry keywords'}

        Generate {company_info.posting_frequency_target} detailed content briefs for this week.
        """

        print("Running brief generation agent...")
        agent_result = await agent.run(brief_input)

        print(f"Brief result type: {type(agent_result)}")
        print(f"Brief result attributes: {dir(agent_result)}")

        # Extract structured output
        briefs_data = agent_result.output
        print(f"Brief data type: {type(briefs_data)}")

        # ✅ Safety: handle if output is dict instead of Pydantic model
        if isinstance(briefs_data, dict):
            try:
                briefs_data = BriefGenerationOutput(**briefs_data)
            except Exception as e:
                raise ValueError(f"Failed to parse briefs_data dict: {e}")

        if not isinstance(briefs_data, BriefGenerationOutput):
            raise ValueError(f"Expected BriefGenerationOutput, got {type(briefs_data)}")

        # ✅ Enforce meta_description <= 160
        briefs_data = truncate_meta_descriptions(briefs_data)

        # Save in state
        state["briefs"] = briefs_data
        state["current_step"] = "brief_generation_done"

        print(f"Brief generation completed: {briefs_data.total_briefs_generated} briefs created")

    except Exception as e:
        print(f"Brief Generation Error: {str(e)}")
        import traceback
        traceback.print_exc()
        state["error"] = f"Brief Generation Failed: {str(e)}"

    return state



# ================== GRAPH BUILDER ==================
content_graph_builder = StateGraph(ContentWorkflowState)

# Add nodes
content_graph_builder.add_node("trend_research", trend_research_node)
content_graph_builder.add_node("content_strategy", content_strategy_node)
content_graph_builder.add_node("brief_generation", brief_generation_node)

# Define workflow edges
content_graph_builder.add_edge(START, "trend_research")
content_graph_builder.add_edge("trend_research", "content_strategy")
content_graph_builder.add_edge("content_strategy", "brief_generation")
content_graph_builder.add_edge("brief_generation", END)

# Compile graph
content_graph = content_graph_builder.compile()