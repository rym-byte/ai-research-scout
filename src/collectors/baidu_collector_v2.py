"""百度搜索采集器 V2 - 使用 HTTP 请求"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class BaiduCollector(BaseCollector):
    """百度搜索采集器 - HTTP 版本"""
    
    platform_name = "baidu"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索百度内容"""
        items = []
        
        try:
            # 百度搜索 URL
            search_url = "https://www.baidu.com/s"
            params = {
                'wd': query,
                'tn': 'json'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.baidu.com/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # 简单解析：提取标题和链接
                        import re
                        
                        # 查找搜索结果
                        # 百度结果格式：<a href="..." ...>标题</a>
                        pattern = r'<a[^>]*href="([^"]+)"[^>]*>\s*<em>([^<]*)</em>\s*([^<]*)</a>'
                        matches = re.findall(pattern, html)
                        
                        for i, (url, em_text, rest_text) in enumerate(matches[:limit]):
                            try:
                                title = em_text + rest_text
                                if title and len(title) > 5:
                                    items.append(SourceItem(
                                        id=f"baidu_{i}_{hash(title) % 10000}",
                                        title=title[:200],
                                        content=title[:500],
                                        url=url if url.startswith('http') else f"https://www.baidu.com{url}",
                                        source='百度',
                                        author='unknown',
                                        created_at=datetime.now(),
                                        score=max(0, 100 - i * 10)
                                    ))
                            except Exception as e:
                                print(f"Parse Baidu result error: {e}")
                                continue
                    else:
                        print(f"Baidu search returned status {response.status}")
                        
        except Exception as e:
            print(f"Baidu search error: {e}")
        
        return items
