"""配置管理模块"""
import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class RedditConfig:
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: str = "AIResearchScout/1.0"


@dataclass
class LLMConfig:
    provider: str = "rule"  # rule / openai / anthropic
    api_key: Optional[str] = None
    model: str = "gpt-4"


@dataclass
class Config:
    """主配置"""
    reddit: RedditConfig = field(default_factory=RedditConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    default_sources: List[str] = field(default_factory=lambda: ["hn", "web"])
    default_limit: int = 10
    output_dir: str = "output"

    @classmethod
    def load(cls, path: str = "config/settings.yaml") -> "Config":
        """加载配置文件"""
        config = cls()

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}

            # Reddit 配置
            if 'reddit' in data:
                config.reddit = RedditConfig(
                    client_id=data['reddit'].get('client_id') or os.getenv('REDDIT_CLIENT_ID'),
                    client_secret=data['reddit'].get('client_secret') or os.getenv('REDDIT_CLIENT_SECRET'),
                    user_agent=data['reddit'].get('user_agent', 'AIResearchScout/1.0')
                )

            # LLM 配置
            if 'llm' in data:
                config.llm = LLMConfig(
                    provider=data['llm'].get('provider', 'rule'),
                    api_key=data['llm'].get('api_key') or os.getenv('LLM_API_KEY'),
                    model=data['llm'].get('model', 'gpt-4')
                )

            # 其他配置
            config.default_sources = data.get('default_sources', ['hn', 'web'])
            config.default_limit = data.get('default_limit', 10)
            config.output_dir = data.get('output_dir', 'output')

        return config

    def ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)