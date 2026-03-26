"""知乎采集器"""
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class ZhihuCollector(BaseCollector):
    """知乎数据采集器"""
    
    platform_name = "zhihu"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索知乎内容"""
        items = []
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # 知乎搜索 API（需要登录，这里使用简化版）
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # 注意：知乎有反爬机制，实际使用需要处理
                url = f'https://www.zhihu.com/api/v4/search_v3?t=general&q={query}'
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get('data', [])[:limit]:
                            if item.get('object', {}).get('type') == 'answer':
                                obj = item['object']
                                items.append(SourceItem(
                                    id=str(obj.get('id', '')),
                                    title=obj.get('question', {}).get('name', 'No title'),
                                    content=obj.get('excerpt', '')[:500],
                                    url=f'https://zhihu.com/question/{obj.get("question", {}).get("id")}/answer/{obj.get("id")}',
                                    source='知乎',
                                    author=obj.get('author', {}).get('name', 'unknown'),
                                    created_at=datetime.now(),
                                    score=obj.get('voteup_count', 0)
                                ))
        except Exception as e:
            print(f"Zhihu Collector error: {e}")
        
        return items