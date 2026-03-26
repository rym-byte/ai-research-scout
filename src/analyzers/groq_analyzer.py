      
"""LLM 深度分析器（支持 DeepSeek/Groq/OpenAI）"""
import os
import requests
from typing import List, Dict, Optional

# 支持多个 LLM 提供商（优先级：DeepSeek > Groq > OpenAI）
PROVIDERS = {
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions", 
        "key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat"
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "model": "llama-3.1-8b-instant"
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key_env": "OPENAI_API_KEY", 
        "model": "gpt-3.5-turbo"
    }
}


class LLMAnalyzer:
    """使用 LLM API 进行深度分析（支持多个提供商）"""
    
    def __init__(self):
        self.model = None
        self.api_key = None
        self.provider_url = None
        self.provider_name = None
        self._init_provider()
    
    def _init_provider(self):
        """初始化提供商，按优先级尝试"""
        for provider_name, config in PROVIDERS.items():
            key = os.environ.get(config["key_env"], "")
            if key:
                self.api_key = key
                self.provider_url = config["url"]
                self.model = config["model"]
                self.provider_name = provider_name
                return
        
        # 没有任何 Key
        self.provider_name = None
        
    def analyze_projects(self, projects: List[Dict], topic: str) -> Dict:
        """分析项目列表，生成深度洞察"""
        if not self.api_key or not self.provider_url:
            return {"error": "No LLM API key configured", "success": False}
        
        # 构建项目摘要
        projects_summary = self._format_projects(projects)
        
        prompt = f"""你是一位资深 AI 技术分析师。请分析以下 AI 项目，提供专业洞察。

## 研究主题
{topic}

## 发现的项目
{projects_summary}

## 请输出
1. **核心趋势** (2-3条)：这些项目反映的 AI 技术趋势
2. **推荐关注** (TOP 3)：最值得深入研究的 3 个项目，说明原因
3. **技术洞察**：关键技术栈、创新点、潜在机会
4. **商业价值**：哪些方向有商业化潜力
5. **风险提示**：需要注意的技术或市场风险

请用中文回答，专业但简洁。"""

        try:
            response = requests.post(
                self.provider_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是一位专业的 AI 技术分析师，擅长发现技术趋势和商业机会。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "analysis": analysis,
                    "model": self.model,
                    "provider": self.provider_name
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text[:200]
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_projects(self, projects: List[Dict]) -> str:
        """格式化项目列表"""
        lines = []
        for i, p in enumerate(projects[:10], 1):
            title = p.get("title", "Unknown")
            url = p.get("url", "")
            source = p.get("source", "")
            lines.append(f"{i}. **{title}**")
            if url:
                lines.append(f"   - URL: {url}")
            if source:
                lines.append(f"   - 来源: {source}")
        return "\n".join(lines) if lines else "暂无项目数据"


# 兼容旧代码的别名
GroqAnalyzer = LLMAnalyzer


def analyze_with_groq(projects: List[Dict], topic: str) -> Dict:
    """便捷函数：使用 LLM 分析项目"""
    analyzer = LLMAnalyzer()
    return analyzer.analyze_projects(projects, topic)

    
