"""X (Twitter) 采集器 - 使用网页版搜索"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class XCollector(BrowserCollector):
    """X (Twitter) 采集器"""
    
    platform_name = "x"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 X 推文"""
        items = []
        
        try:
            # X 搜索 URL
            search_url = f"https://x.com/search?q={query.replace(' ', '%20')}&f=live"
            
            if not await self._browser_open(search_url):
                print("Failed to open X")
                return items
            
            # 等待页面加载（X 需要较长时间）
            await self._browser_wait(3000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get X snapshot")
                return items
            
            # 解析 X 搜索结果
            refs = snapshot.get('data', {}).get('refs', {})
            
            tweet_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # X 推文内容
                if role in ['article', 'link'] and name and len(name) > 10:
                    tweet_refs.append({
                        'ref': ref_id,
                        'title': name[:200]
                    })
            
            # 提取结果
            for i, tweet in enumerate(tweet_refs[:limit]):
                try:
                    title = tweet['title']
                    
                    items.append(SourceItem(
                        id=f"x_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=f"https://x.com/search?q={query.replace(' ', '%20')}",
                        source='X',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse X result error: {e}")
                    continue
            
        except Exception as e:
            print(f"X search error: {e}")
        
        return items
