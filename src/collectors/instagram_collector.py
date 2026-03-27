"""Instagram 采集器 - 使用网页搜索"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class InstagramCollector(BrowserCollector):
    """Instagram 采集器"""
    
    platform_name = "instagram"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 Instagram 内容"""
        items = []
        
        try:
            # Instagram 搜索标签或账户
            # Instagram 网页版功能有限，主要搜索标签
            search_url = f"https://www.instagram.com/explore/tags/{query.replace(' ', '')}/"
            
            if not await self._browser_open(search_url):
                print("Failed to open Instagram")
                return items
            
            # 等待页面加载
            await self._browser_wait(3000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Instagram snapshot")
                return items
            
            # 解析 Instagram 页面
            refs = snapshot.get('data', {}).get('refs', {})
            
            result_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # Instagram 帖子描述
                if role in ['link', 'article'] and name and len(name) > 3:
                    result_refs.append({
                        'ref': ref_id,
                        'title': name
                    })
            
            # 提取结果
            for i, result in enumerate(result_refs[:limit]):
                try:
                    title = result['title']
                    
                    items.append(SourceItem(
                        id=f"ig_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=search_url,
                        source='Instagram',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse Instagram result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Instagram search error: {e}")
        
        return items
