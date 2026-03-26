"""Twitter/X 采集器"""
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class TwitterCollector(BaseCollector):
    """Twitter/X 数据采集器"""
    
    platform_name = "twitter"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索推文"""
        items = []
        try:
            import tweepy
            
            if not all([self.config.get('api_key'), self.config.get('api_secret')]):
                print("Twitter API credentials not configured")
                return items
            
            client = tweepy.Client(
                consumer_key=self.config['api_key'],
                consumer_secret=self.config['api_secret'],
                access_token=self.config.get('access_token'),
                access_token_secret=self.config.get('access_token_secret')
            )
            
            tweets = client.search_recent_tweets(query=query, max_results=min(limit, 100))
            
            if tweets.data:
                for tweet in tweets.data:
                    items.append(SourceItem(
                        id=str(tweet.id),
                        title=tweet.text[:100] + '...' if len(tweet.text) > 100 else tweet.text,
                        content=tweet.text,
                        url=f'https://twitter.com/i/web/status/{tweet.id}',
                        source='Twitter',
                        author=str(tweet.author_id) if hasattr(tweet, 'author_id') else 'unknown',
                        created_at=datetime.now(),
                        score=tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0
                    ))
        except Exception as e:
            print(f"Twitter Collector error: {e}")
        
        return items