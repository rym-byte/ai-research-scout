"""Hacker News 采集器"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class HNCollector(BaseCollector):
    """Hacker News 数据采集器"""
    
    platform_name = "hacker_news"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 HN 帖子"""
        items = []
        try:
            async with aiohttp.ClientSession() as session:
                # 获取热门帖子
                async with session.get('https://hacker-news.firebaseio.com/v0/topstories.json') as resp:
                    story_ids = await resp.json()
                    story_ids = story_ids[:limit * 2]
                
                # 获取每个帖子的详情
                for story_id in story_ids[:limit]:
                    try:
                        async with session.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json') as resp:
                            story = await resp.json()
                            if story and 'title' in story:
                                # 简单关键词匹配
                                if query.lower() in story['title'].lower():
                                    items.append(SourceItem(
                                        id=str(story['id']),
                                        title=story['title'],
                                        content=story.get('text', '')[:500],
                                        url=story.get('url', f'https://news.ycombinator.com/item?id={story["id"]}'),
                                        source='Hacker News',
                                        author=story.get('by', 'unknown'),
                                        created_at=datetime.fromtimestamp(story['time']),
                                        score=story.get('score', 0)
                                    ))
                    except:
                        continue
        except Exception as e:
            print(f"HN Collector error: {e}")
        
        return items[:limit]