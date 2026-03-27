"""百度搜索采集器"""
from typing import List
from datetime import datetime
from .browser_collector import BrowserCollector
from . import SourceItem


class BaiduCollector(BrowserCollector):
    """百度搜索采集器"""
    
    platform_name = "baidu"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索百度内容"""
        items = []
        
        try:
            # 打开百度搜索
            search_url = f"https://www.baidu.com/s?wd={query.replace(' ', '+')}"
            if not await self._browser_open(search_url):
                print("Failed to open Baidu")
                return items
            
            # 等待页面加载
            await self._browser_wait(2000)
            
            # 获取页面快照
            snapshot = await self._browser_snapshot(interactive=True)
            if not snapshot:
                print("Failed to get Baidu snapshot")
                return items
            
            # 解析搜索结果
            # 百度搜索结果通常在 .result 或 [tpl] 属性中
            refs = snapshot.get('data', {}).get('refs', {})
            
            # 查找搜索结果标题和链接
            result_refs = []
            for ref_id, ref_info in refs.items():
                role = ref_info.get('role', '')
                name = ref_info.get('name', '')
                
                # 百度结果标题通常是 heading 或 link
                if role in ['heading', 'link'] and name:
                    result_refs.append({
                        'ref': ref_id,
                        'title': name,
                        'info': ref_info
                    })
            
            # 提取前 limit 个结果
            for i, result in enumerate(result_refs[:limit]):
                try:
                    title = result['title']
                    ref = result['ref']
                    
                    # 获取链接地址
                    # 百度结果需要点击或从属性获取
                    url = f"https://www.baidu.com/s?wd={query.replace(' ', '+')}"  # 默认使用搜索页
                    
                    items.append(SourceItem(
                        id=f"baidu_{i}_{hash(title) % 10000}",
                        title=title[:200],
                        content=title[:500],  # 百度需要额外获取摘要
                        url=url,
                        source='百度',
                        author='unknown',
                        created_at=datetime.now(),
                        score=100 - i * 10  # 排名越前分数越高
                    ))
                except Exception as e:
                    print(f"Parse Baidu result error: {e}")
                    continue
            
        except Exception as e:
            print(f"Baidu search error: {e}")
        
        return items
