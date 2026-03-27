"""B站采集器 - 使用B站搜索API"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class BilibiliCollector(BaseCollector):
    """B站视频采集器"""
    
    platform_name = "bilibili"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索B站视频"""
        items = []
        
        try:
            # B站搜索API（无需登录）
            search_url = "https://api.bilibili.com/x/web-interface/search/all"
            params = {
                'keyword': query,
                'page': 1,
                'pagesize': limit
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://search.bilibili.com/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('data', {}).get('result', []):
                            # 查找视频结果
                            for result_type in data['data']['result']:
                                if result_type.get('result_type') == 'video':
                                    videos = result_type.get('data', [])
                                    
                                    for i, video in enumerate(videos[:limit]):
                                        try:
                                            bvid = video.get('bvid', '')
                                            title = video.get('title', '').replace('<em class=\"keyword\">', '').replace('</em>', '')
                                            description = video.get('description', '')
                                            author = video.get('author', 'unknown')
                                            pubdate = video.get('pubdate', 0)
                                            play_count = video.get('play', 0)
                                            
                                            # 转换播放量
                                            if isinstance(play_count, str):
                                                play_count = play_count.replace('万', '0000').replace('.', '')
                                                try:
                                                    play_count = int(play_count)
                                                except:
                                                    play_count = 0
                                            
                                            items.append(SourceItem(
                                                id=f"bilibili_{bvid}",
                                                title=title[:200],
                                                content=description[:500],
                                                url=f"https://www.bilibili.com/video/{bvid}",
                                                source='B站',
                                                author=author,
                                                created_at=datetime.fromtimestamp(pubdate) if pubdate else datetime.now(),
                                                score=play_count if isinstance(play_count, int) else 0
                                            ))
                                        except Exception as e:
                                            print(f"Parse Bilibili video error: {e}")
                                            continue
                                    break
                                    
        except Exception as e:
            print(f"Bilibili search error: {e}")
        
        return items
