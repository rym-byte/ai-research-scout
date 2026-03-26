"""Reddit 采集器"""
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class RedditCollector(BaseCollector):
    """Reddit 数据采集器"""
    
    platform_name = "reddit"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.reddit = None
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 Reddit 帖子"""
        items = []
        try:
            import praw
            
            if not self.reddit:
                self.reddit = praw.Reddit(
                    client_id=self.config.get('client_id', ''),
                    client_secret=self.config.get('client_secret', ''),
                    user_agent=self.config.get('user_agent', 'AIResearchScout/1.0')
                )
            
            # 搜索相关 subreddit
            for submission in self.reddit.subreddit('all').search(query, limit=limit):
                items.append(SourceItem(
                    id=str(submission.id),
                    title=submission.title,
                    content=submission.selftext[:500] if submission.selftext else '',
                    url=f'https://reddit.com{submission.permalink}',
                    source='Reddit',
                    author=str(submission.author) if submission.author else 'unknown',
                    created_at=datetime.fromtimestamp(submission.created_utc),
                    score=submission.score
                ))
        except Exception as e:
            print(f"Reddit Collector error: {e}")
        
        return items