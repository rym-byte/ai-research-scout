      
"""Groq LLM 深度分析器"""
import os
import requests
from typing import List, Dict, Optional

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqAnalyzer:
    """使用 Groq API 进行深度分析"""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.model = model
        self.api_key = GROQ_API_KEY
        
    def analyze_projects(self, projects: List[Dict], topic: str) -> Dict:
        """分析项目列表，生成深度洞察"""
        if not self.api_key:
            return {"error": "GROQ_API_KEY not configured"}
        
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
                GROQ_API_URL,
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
                    "model": self.model
                }
            else:
                return {
                    "success": False,
                    "error": f"Groq API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_projects(self, projects: List[Dict]) -> str:
        """格式化项目列表"""
        lines = []
        for i, p in enumerate(projects[:10], 1):  # 最多10个
            title = p.get("title", "Unknown")
            url = p.get("url", "")
            source = p.get("source", "")
            lines.append(f"{i}. **{title}**")
            if url:
                lines.append(f"   - URL: {url}")
            if source:
                lines.append(f"   - 来源: {source}")
        return "\n".join(lines) if lines else "暂无项目数据"


def analyze_with_groq(projects: List[Dict], topic: str) -> Dict:
    """便捷函数：使用 Groq 分析项目"""
    analyzer = GroqAnalyzer()
    return analyzer.analyze_projects(projects, topic)

    
