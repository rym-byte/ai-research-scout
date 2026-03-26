      
"""LLM 深度分析器"""
import os
import requests
from typing import List, Dict

PROVIDERS = {
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat"
    }
}


class LLMAnalyzer:
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.url = PROVIDERS["deepseek"]["url"]
        self.model = PROVIDERS["deepseek"]["model"]

    def analyze_projects(self, projects: List[Dict], topic: str) -> Dict:
        if not self.api_key:
            return {"error": "DEEPSEEK_API_KEY not configured", "success": False}

        summary = "\n".join([f"{i+1}. {p.get('title', '')}" for i, p in enumerate(projects[:10])])
        prompt = f"分析以下AI项目:\n{summary}\n\n给出核心趋势、TOP3推荐、技术洞察、商业价值、风险提示"

        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000
                },
                timeout=60
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "analysis": response.json()["choices"][0]["message"]["content"]
                }
            return {
                "success": False,
                "error": f"API error: {response.status_code}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


GroqAnalyzer = LLMAnalyzer


def analyze_with_groq(projects: List[Dict], topic: str) -> Dict:
    return LLMAnalyzer().analyze_projects(projects, topic)

    
