"""搜狗搜索采集器 - HTTP 版本"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class SogouCollector(BaseCollector):
    """搜狗搜索采集器"""
    
    platform_name = "sogou"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索搜狗内容"""
        items = []
        
        try:
            search_url = "https://www.sogou.com/web"
            params = {
                'query': query,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        from bs4 import BeautifulSoup
                        import re
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 查找搜索结果
                        result_containers = soup.find_all(['div', 'li'], class_=re.compile('vrwrap|result'))
                        
                        for i, container in enumerate(result_containers[:limit]):
                            try:
                                title_tag = container.find('a')
                                if not title_tag:
                                    continue
                                
                                title = title_tag.get_text(strip=True)
                                href = title_tag.get('href', '')
                                
                                if not title or len(title) < 3:
                                    continue
                                
                                items.append(SourceItem(
                                    id=f"sogou_{i}_{hash(title) % 10000}",
                                    title=title[:200],
                                    content=title[:500],
                                    url=href if href.startswith('http') else f"https://www.sogou.com{href}",
                                    source='搜狗',
                                    author='unknown',
                                    created_at=datetime.now(),
                                    score=max(0, 100 - i * 10)
                                ))
                            except Exception as e:
                                print(f"Parse Sogou result error: {e}")
                                continue
                    else:
                        print(f"Sogou search returned status {response.status}")
                        
        except Exception as e:
            print(f"Sogou search error: {e}")
        
        return items
