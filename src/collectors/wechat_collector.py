"""微信搜一搜采集器 - 使用搜狗微信搜索"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class WechatCollector(BrowserCollector):
    """微信搜一搜采集器（通过搜狗微信搜索）"""
    
    platform_name = "wechat"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索微信公众号文章"""
        items = []
        
        try:
            # 使用搜狗微信搜索
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query.replace(' ', '+')}"
            
            if not await self._browser_open(search_url):
                print("Failed to open Wechat search")
                return items
            
            # 等待页面加载
            await self._browser_wait(2000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Wechat snapshot")
                return items
            
            # 解析微信搜索结果
            refs = snapshot.get('data', {}).get('refs', {})
            
            result_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # 微信文章标题
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
                        id=f"wechat_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=search_url,
                        source='微信',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse Wechat result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Wechat search error: {e}")
        
        return items
