"""Web 搜索数据采集器"""
import aiohttp
from typing import List, Dict, Any
from datetime import datetime
from duckduckgo_search import DDGS
import asyncio


class WebCollector:
    """Web 搜索采集器（使用 DuckDuckGo）"""

    def __init__(self):
        self.ddgs = DDGS()

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索 Web"""
        results = []

        try:
            # DuckDuckGo 搜索
            search_results = list(self.ddgs.text(query, max_results=limit))

            for item in search_results:
                results.append({
                    'id': item.get('href', ''),
                    'title': item.get('title', ''),
                    'url': item.get('href', ''),
                    'score': 0,  # Web 搜索没有分数
                    'author': 'unknown',
                    'time': datetime.now(),
                    'comments': 0,
                    'text': item.get('body', ''),
                    'source': 'web'
                })

        except Exception as e:
            print(f"Web search error: {e}")

        return results

    async def get_details(self, item_id: str) -> Dict[str, Any]:
        """Web 搜索不需要详情"""
        return {}

    async def close(self):
        pass