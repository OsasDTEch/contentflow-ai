"""
Fixed Google Trends Implementation for ContentFlow AI
===================================================
"""

import time
import random
from pytrends.request import TrendReq
import pandas as pd
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleTrendsResearcher:
    """Robust Google Trends research with error handling"""

    def __init__(self):
        self.pytrends = None
        self.initialize_connection()

    def initialize_connection(self):
        """Initialize Google Trends connection with proper configuration"""
        try:
            # ✅ CORRECTED CONFIGURATION
            self.pytrends = TrendReq(
                hl='en-US',  # Language
                tz=360,  # Timezone offset
                timeout=(10, 25),  # Connection timeout
                proxies=None,  # ❌ Remove proxies for testing
                retries=3,  # Increase retries
                backoff_factor=0.5,  # Longer backoff
                requests_args={}  # ❌ Remove verify=False
            )
            logger.info("✅ Google Trends connection initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Trends: {e}")
            raise

    def research_trends(self, keywords: List[str], company_industry: str) -> List[Dict[str, Any]]:
        """
        Research trends with proper error handling and rate limiting
        """
        trends_data = []

        for keyword in keywords:
            try:
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(2, 5))

                trend_data = self.get_single_trend(keyword, company_industry)
                if trend_data:
                    trends_data.append(trend_data)

            except Exception as e:
                logger.warning(f"⚠️ Failed to get trend data for '{keyword}': {e}")
                continue

        return trends_data

    def get_single_trend(self, keyword: str, industry: str) -> Dict[str, Any]:
        """Get trend data for a single keyword"""

        try:
            # ✅ CORRECTED: Build payload with proper parameters
            self.pytrends.build_payload(
                kw_list=[keyword],  # Single keyword in list
                cat=0,  # All categories
                timeframe='today 3-m',  # Last 3 months (more reliable than 5-y)
                geo='US',  # Specify geography
                gprop=''  # Web search
            )

            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()

            if interest_over_time.empty:
                logger.warning(f"No data found for keyword: {keyword}")
                return None

            # Calculate trend metrics
            recent_values = interest_over_time[keyword].tail(4)  # Last 4 weeks
            older_values = interest_over_time[keyword].head(4)  # First 4 weeks

            recent_avg = recent_values.mean()
            older_avg = older_values.mean()
            max_interest = interest_over_time[keyword].max()

            # Determine trend direction
            if recent_avg > older_avg * 1.2:
                trend_direction = "rising"
            elif recent_avg < older_avg * 0.8:
                trend_direction = "falling"
            else:
                trend_direction = "stable"

            # Get related queries for content ideas
            related_queries = self.get_related_queries(keyword)

            return {
                "topic": keyword,
                "search_volume": int(max_interest),
                "trend_direction": trend_direction,
                "recent_interest": int(recent_avg),
                "growth_rate": ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0,
                "related_queries": related_queries,
                "data_source": "google_trends",
                "relevance_score": self.calculate_relevance_score(keyword, industry),
                "last_updated": pd.Timestamp.now()
            }

        except Exception as e:
            logger.error(f"Error getting trend data for '{keyword}': {e}")
            return None

    def get_related_queries(self, keyword: str) -> List[str]:
        """Get related queries for content inspiration"""
        try:
            related_queries = self.pytrends.related_queries()

            if keyword in related_queries and related_queries[keyword]['top'] is not None:
                # Get top 5 related queries
                top_queries = related_queries[keyword]['top']['query'].head(5).tolist()
                return top_queries

            return []

        except Exception as e:
            logger.warning(f"Could not get related queries for '{keyword}': {e}")
            return []

    def calculate_relevance_score(self, keyword: str, industry: str) -> float:
        """Calculate how relevant the keyword is to the company's industry"""

        # Industry-specific keyword mapping
        industry_keywords = {
            "SaaS": ["software", "cloud", "api", "automation", "AI", "platform", "tool"],
            "E-commerce": ["shopping", "retail", "store", "product", "customer", "sale"],
            "Healthcare": ["health", "medical", "patient", "care", "treatment", "wellness"],
            "Finance": ["financial", "money", "investment", "banking", "payment", "crypto"],
            "Marketing": ["advertising", "brand", "content", "social", "campaign", "analytics"]
        }

        relevant_terms = industry_keywords.get(industry, [])

        # Calculate relevance based on keyword overlap
        keyword_lower = keyword.lower()
        relevance_score = 0.5  # Base relevance

        for term in relevant_terms:
            if term in keyword_lower:
                relevance_score += 0.1

        return min(relevance_score, 1.0)


# =============================================================================
# TESTING YOUR FIXED CODE
# =============================================================================

def test_google_trends():
    """Test the fixed Google Trends implementation"""

    try:
        researcher = GoogleTrendsResearcher()

        # Test with your blockchain keyword
        test_keywords = ["Blockchain", "AI automation", "SaaS tools"]

        print("🔍 Testing Google Trends research...")
        trends = researcher.research_trends(test_keywords, "SaaS")

        print(f"\n✅ Successfully found {len(trends)} trends:")
        for trend in trends:
            print(f"  - {trend['topic']}: {trend['trend_direction']} trend, score: {trend['search_volume']}")

        return trends

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


# =============================================================================
# ALTERNATIVE: SERPER API (More Reliable)
# =============================================================================

import requests


class SerperTrendsResearcher:
    """Alternative using Serper API (more reliable than Google Trends)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"

    def research_trends(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Research using Serper API (more stable)"""

        trends_data = []

        for keyword in keywords:
            try:
                # Search for recent articles about the keyword
                response = requests.post(
                    self.base_url,
                    headers={
                        'X-API-KEY': self.api_key,
                        'Content-Type': 'application/json'
                    },
                    json={
                        'q': f"{keyword} trends 2024",
                        'num': 10,
                        'gl': 'us',
                        'hl': 'en'
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    trend_info = {
                        "topic": keyword,
                        "search_results": len(data.get('organic', [])),
                        "trend_direction": self.analyze_trend_from_results(data),
                        "data_source": "serper_api",
                        "related_searches": data.get('relatedSearches', []),
                        "news_mentions": len(data.get('news', [])),
                    }

                    trends_data.append(trend_info)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Serper API error for '{keyword}': {e}")
                continue

        return trends_data

    def analyze_trend_from_results(self, data: Dict) -> str:
        """Analyze trend direction from search results"""

        recent_keywords = ["2024", "new", "latest", "trending", "growing", "rising"]
        declining_keywords = ["dead", "dying", "obsolete", "replaced", "declining"]

        organic_results = data.get('organic', [])

        recent_count = 0
        declining_count = 0

        for result in organic_results[:5]:  # Check top 5 results
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()

            text = f"{title} {snippet}"

            for keyword in recent_keywords:
                if keyword in text:
                    recent_count += 1

            for keyword in declining_keywords:
                if keyword in text:
                    declining_count += 1

        if recent_count > declining_count:
            return "rising"
        elif declining_count > recent_count:
            return "falling"
        else:
            return "stable"


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":

    print("🚀 Testing Fixed Google Trends Implementation")
    print("=" * 50)

    # Test 1: Fixed Google Trends
    trends = test_google_trends()

    if not trends:
        print("\n⚠️  Google Trends failed, trying alternative...")

        # Test 2: Serper API (you need to get API key from serper.dev)
        # serper_researcher = SerperTrendsResearcher("YOUR_SERPER_API_KEY")
        # trends = serper_researcher.research_trends(["Blockchain", "AI automation"])
        # print(f"✅ Serper found {len(trends)} trends")

"""
🔧 FIXES APPLIED:

1. ❌ Fixed proxy configuration (removed problematic proxy)
2. ❌ Removed SSL verification disable 
3. ✅ Added proper error handling and retries
4. ✅ Added rate limiting with random delays
5. ✅ Changed timeframe to 'today 3-m' (more reliable)
6. ✅ Added geo='US' for better results
7. ✅ Included alternative Serper API option
8. ✅ Added trend calculation logic
9. ✅ Added related queries extraction
10. ✅ Added relevance scoring

🚨 COMMON GOOGLE TRENDS ISSUES:
- Rate limiting (add delays)
- IP blocking (use rotating proxies in production)
- Empty results (try different keywords/timeframes)
- Connection timeouts (increase timeout values)

💡 RECOMMENDATION:
For production, consider using Serper API ($50/month) instead of 
Google Trends - much more reliable and no rate limiting issues.
"""