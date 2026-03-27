"""抖音采集器 - 使用抖音网页搜索"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class DouyinCollector(BrowserCollector):
    """抖音视频采集器"""
    
    platform_name = "douyin"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索抖音视频"""
        items = []
        
        try:
            # 抖音网页版搜索
            # 注意：抖音网页版需要处理反爬，这里使用简化版本
            search_url = f"https://www.douyin.com/search/{query.replace(' ', '%20')}"
            
            if not await self._browser_open(search_url):
                print("Failed to open Douyin")
                return items
            
            # 等待页面加载（抖音需要较长时间）
            await self._browser_wait(3000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Douyin snapshot")
                return items
            
            # 解析抖音搜索结果
            # 抖音视频卡片通常包含标题、作者、点赞数
            refs = snapshot.get('data', {}).get('refs', {})
            
            video_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # 查找视频标题
                if role in ['heading', 'link'] and name and len(name) > 5:
                    video_refs.append({
                        'ref': ref_id,
                        'title': name
                    })
            
            # 提取结果
            for i, video in enumerate(video_refs[:limit]):
                try:
                    title = video['title']
                    
                    items.append(SourceItem(
                        id=f"douyin_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=search_url,  # 抖音链接需要额外处理
                        source='抖音',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse Douyin result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Douyin search error: {e}")
        
        return items
