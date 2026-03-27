"""小红书采集器 - 使用小红书网页搜索"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class XiaohongshuCollector(BrowserCollector):
    """小红书笔记采集器"""
    
    platform_name = "xiaohongshu"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索小红书笔记"""
        items = []
        
        try:
            # 小红书网页版搜索
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={query.replace(' ', '%20')}"
            
            if not await self._browser_open(search_url):
                print("Failed to open Xiaohongshu")
                return items
            
            # 等待页面加载
            await self._browser_wait(3000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Xiaohongshu snapshot")
                return items
            
            # 解析小红书搜索结果
            refs = snapshot.get('data', {}).get('refs', {})
            
            note_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # 查找笔记标题
                if role in ['heading', 'link'] and name and len(name) > 3:
                    note_refs.append({
                        'ref': ref_id,
                        'title': name
                    })
            
            # 提取结果
            for i, note in enumerate(note_refs[:limit]):
                try:
                    title = note['title']
                    
                    items.append(SourceItem(
                        id=f"xhs_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],
                        url=search_url,
                        source='小红书',
                        author='unknown',
                        created_at=datetime.now(),
                        score=max(0, 100 - i * 10)
                    ))
                except Exception as e:
                    print(f"Parse Xiaohongshu result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Xiaohongshu search error: {e}")
        
        return items
