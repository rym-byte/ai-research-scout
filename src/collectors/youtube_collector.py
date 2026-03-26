"""YouTube 采集器"""
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class YouTubeCollector(BaseCollector):
    """YouTube 数据采集器"""
    
    platform_name = "youtube"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 YouTube 视频"""
        items = []
        try:
            from googleapiclient.discovery import build
            
            if not self.config.get('api_key'):
                print("YouTube API key not configured")
                return items
            
            youtube = build('youtube', 'v3', developerKey=self.config['api_key'])
            
            search_response = youtube.search().list(
                q=query,
                part='snippet',
                maxResults=limit,
                type='video'
            ).execute()
            
            for search_result in search_response.get('items', []):
                video_id = search_result['id']['videoId']
                items.append(SourceItem(
                    id=video_id,
                    title=search_result['snippet']['title'],
                    content=search_result['snippet']['description'][:500],
                    url=f'https://youtube.com/watch?v={video_id}',
                    source='YouTube',
                    author=search_result['snippet']['channelTitle'],
                    created_at=datetime.fromisoformat(search_result['snippet']['publishedAt'].replace('Z', '+00:00')),
                    score=0
                ))
        except Exception as e:
            print(f"YouTube Collector error: {e}")
        
        return items