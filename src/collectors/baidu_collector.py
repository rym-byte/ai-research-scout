"""百度搜索采集器 - HTTP 版本"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class BaiduCollector(BaseCollector):
    """百度搜索采集器"""
    
    platform_name = "baidu"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索百度内容"""
        items = []
        
        try:
            # 使用百度搜索
            search_url = "https://www.baidu.com/s"
            params = {
                'wd': query,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': 'https://www.baidu.com/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # 解析搜索结果
                        import re
                        from bs4 import BeautifulSoup
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 查找搜索结果容器
                        result_containers = soup.find_all(['div', 'article'], class_=re.compile('result|c-container'))
                        
                        for i, container in enumerate(result_containers[:limit]):
                            try:
                                # 查找标题链接
                                title_tag = container.find('a')
                                if not title_tag:
                                    continue
                                
                                title = title_tag.get_text(strip=True)
                                href = title_tag.get('href', '')
                                
                                if not title or len(title) < 3:
                                    continue
                                
                                # 查找摘要
                                abstract_tag = container.find(['span', 'div', 'p'], class_=re.compile('content-right|c-abstract'))
                                abstract = abstract_tag.get_text(strip=True) if abstract_tag else title
                                
                                items.append(SourceItem(
                                    id=f"baidu_{i}_{hash(title) % 10000}",
                                    title=title[:200],
                                    content=abstract[:500],
                                    url=href if href.startswith('http') else f"https://www.baidu.com{href}",
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
