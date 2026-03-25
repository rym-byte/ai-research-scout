"""Hacker News 数据采集器"""
import aiohttp
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class HNItem:
    """HN 数据项"""
    id: int
    title: str
    url: str
    score: int
    author: str
    time: datetime
    comments: int
    text: str = ""


class HNCollector:
    """Hacker News 采集器"""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.session = None

    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索 HN（使用官方 API + 过滤）"""
        session = await self._get_session()

        # 获取最新故事 ID
        async with session.get(f"{self.BASE_URL}/newstories.json") as resp:
            story_ids = await resp.json()

        # 获取故事详情并过滤
        results = []
        query_lower = query.lower()

        for story_id in story_ids[:200]:  # 检查最近 200 条
            if len(results) >= limit:
                break

            try:
                async with session.get(f"{self.BASE_URL}/item/{story_id}.json") as resp:
                    item = await resp.json()

                if not item:
                    continue

                title = item.get('title', '').lower()

                # 简单关键词匹配
                if any(kw in title for kw in query_lower.split()):
                    results.append({
                        'id': item.get('id'),
                        'title': item.get('title', ''),
                        'url': item.get('url') or f"https://news.ycombinator.com/item?id={item.get('id')}",
                        'score': item.get('score', 0),
                        'author': item.get('by', 'unknown'),
                        'time': datetime.fromtimestamp(item.get('time', 0)),
                        'comments': item.get('descendants', 0),
                        'text': item.get('text', ''),
                        'source': 'hacker_news'
                    })
            except Exception:
                continue

        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    async def get_details(self, item_id: int) -> Dict[str, Any]:
        """获取详情"""
        session = await self._get_session()
        async with session.get(f"{self.BASE_URL}/item/{item_id}.json") as resp:
            item = await resp.json()

        return {
            'id': item.get('id'),
            'title': item.get('title', ''),
            'url': item.get('url') or f"https://news.ycombinator.com/item?id={item.get('id')}",
            'score': item.get('score', 0),
            'author': item.get('by', 'unknown'),
            'time': datetime.fromtimestamp(item.get('time', 0)),
            'comments': item.get('descendants', 0),
            'text': item.get('text', ''),
            'source': 'hacker_news'
        }

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None