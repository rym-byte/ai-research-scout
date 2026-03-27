"""搜狗搜索采集器"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class SogouCollector(BrowserCollector):
    """搜狗搜索采集器"""
    
    platform_name = "sogou"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索搜狗内容"""
        items = []
        
        try:
            # 搜狗搜索
            search_url = f"https://www.sogou.com/web?query={query.replace(' ', '+')}"
            
            if not await self._browser_open(search_url):
                print("Failed to open Sogou")
                return items
            
            # 等待页面加载
            await self._browser_wait(2000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Sogou snapshot")
                return items
            
            # 解析搜狗搜索结果
            refs = snapshot.get('data', {}).get('refs', {})
            
            result_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # 搜狗结果标题
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
                        id=f"sogou_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=search_url,
                        source='搜狗',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse Sogou result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Sogou search error: {e}")
        
        return items
