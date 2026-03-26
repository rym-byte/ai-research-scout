"""数据采集器基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SourceItem:
    """数据源条目"""
    id: str
    title: str
    content: str
    url: str
    source: str
    author: str
    created_at: datetime
    score: int = 0
    metadata: Dict[str, Any] = None


class BaseCollector(ABC):
    """数据采集器基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称"""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[SourceItem]:
        """搜索相关内容"""
        pass
    
    async def close(self):
        """清理资源"""
        pass