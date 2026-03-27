"""微信搜一搜采集器 - 使用搜狗微信搜索 HTTP 版本"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class WechatCollector(BaseCollector):
    """微信搜一搜采集器（通过搜狗微信搜索）"""
    
    platform_name = "wechat"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索微信公众号文章"""
        items = []
        
        try:
            # 使用搜狗微信搜索
            search_url = "https://weixin.sogou.com/weixin"
            params = {
                'type': '2',  # 搜索文章
                'query': query,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': 'https://weixin.sogou.com/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        from bs4 import BeautifulSoup
                        import re
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 查找微信文章结果
                        result_containers = soup.find_all('li', class_=re.compile('result|wx-rb'))
                        
                        for i, container in enumerate(result_containers[:limit]):
                            try:
                                title_tag = container.find('a', class_=re.compile('title|tit'))
                                if not title_tag:
                                    title_tag = container.find('a')
                                
                                if not title_tag:
                                    continue
                                
                                title = title_tag.get_text(strip=True)
                                href = title_tag.get('href', '')
                                
                                # 清理标题中的高亮标签
                                title = re.sub(r'<em>|</em>', '', title)
                                
                                if not title or len(title) < 3:
                                    continue
                                
                                # 查找摘要
                                abstract_tag = container.find('p', class_=re.compile('summary|abs'))
                                abstract = abstract_tag.get_text(strip=True) if abstract_tag else title
                                abstract = re.sub(r'<em>|</em>', '', abstract)
                                
                                items.append(SourceItem(
                                    id=f"wechat_{i}_{hash(title) % 10000}",
                                    title=title[:200],
                                    content=abstract[:500],
                                    url=f"https://weixin.sogou.com{href}" if not href.startswith('http') else href,
                                    source='微信',
                                    author='unknown',
                                    created_at=datetime.now(),
                                    score=max(0, 100 - i * 10)
                                ))
                            except Exception as e:
                                print(f"Parse Wechat result error: {e}")
                                continue
                    else:
                        print(f"Wechat search returned status {response.status}")
                        
        except Exception as e:
            print(f"Wechat search error: {e}")
        
        return items
