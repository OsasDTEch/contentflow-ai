from dotenv import load_dotenv
from pydantic_ai import Agent
from  pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.google import GoogleModel, GoogleProvider
import os
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
provider= GoogleProvider(api_key=GOOGLE_API_KEY)
model = GoogleModel(model_name='gemini-2.5-flash',provider=provider)

web_search_agent= Agent(
    model,
    tools=[duckduckgo_search_tool()],
    system_prompt="""
    You are a web search assistant. When given a query:
1. Use the duckduckgo_search_tool tool to find information
2. Summarize the key findings
3. Focus on recent/relevant information
4. Keep responses concise and actionable"""
)


async def web_search(query: str):
    result = await web_search_agent.run(query)

    # Main model response


    return result


if __name__ == '__main__':
    import asyncio
    asyncio.run(web_search(query='Find the latest news articles about the iPhone 17 Pro’s durability issues from the past 24 hours and summarize them'))