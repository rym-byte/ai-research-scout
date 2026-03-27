"""Facebook 采集器 - 使用网页搜索"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class FacebookCollector(BrowserCollector):
    """Facebook 采集器"""
    
    platform_name = "facebook"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 Facebook 内容"""
        items = []
        
        try:
            # Facebook 搜索需要登录，这里使用简化版本
            # 实际使用时可能需要处理登录状态
            search_url = f"https://www.facebook.com/search/top?q={query.replace(' ', '%20')}"
            
            if not await self._browser_open(search_url):
                print("Failed to open Facebook")
                return items
            
            # 等待页面加载
            await self._browser_wait(3000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Facebook snapshot")
                return items
            
            # 解析 Facebook 搜索结果
            refs = snapshot.get('data', {}).get('refs', {})
            
            result_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # Facebook 帖子/页面标题
                if role in ['heading', 'link'] and name and len(name) > 5:
                    result_refs.append({
                        'ref': ref_id,
                        'title': name
                    })
            
            # 提取结果
            for i, result in enumerate(result_refs[:limit]):
                try:
                    title = result['title']
                    
                    items.append(SourceItem(
                        id=f"fb_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=search_url,
                        source='Facebook',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse Facebook result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Facebook search error: {e}")
        
        return items
