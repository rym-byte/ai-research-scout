"""GitHub 采集器"""
import aiohttp
from typing import List
from datetime import datetime
from . import BaseCollector, SourceItem


class GitHubCollector(BaseCollector):
    """GitHub 数据采集器"""
    
    platform_name = "github"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索 GitHub 仓库"""
        items = []
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.config.get('token'):
                    headers['Authorization'] = f'token {self.config["token"]}'
                
                async with session.get(
                    f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={limit}',
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for repo in data.get('items', []):
                            items.append(SourceItem(
                                id=str(repo['id']),
                                title=repo['name'],
                                content=repo.get('description', '') or '',
                                url=repo['html_url'],
                                source='GitHub',
                                author=repo['owner']['login'],
                                created_at=datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00')),
                                score=repo['stargazers_count']
                            ))
        except Exception as e:
            print(f"GitHub Collector error: {e}")
        
        return items