"""Web 搜索采集器"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class WebCollector(BaseCollector):
    """Web 搜索数据采集器"""
    
    platform_name = "web"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索网页内容"""
        items = []
        try:
            # 使用 DuckDuckGo 搜索
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=limit)
                for result in results:
                    items.append(SourceItem(
                        id=result.get('href', '')[:50],
                        title=result.get('title', 'No title'),
                        content=result.get('body', '')[:500],
                        url=result.get('href', ''),
                        source='Web',
                        author='unknown',
                        created_at=datetime.now(),
                        score=0
                    ))
        except Exception as e:
            print(f"Web Collector error: {e}")
        
        return items