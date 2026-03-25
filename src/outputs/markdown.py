"""Markdown 报告输出"""
from typing import Dict, Any
from datetime import datetime
from ..analyzers.synthesizer import ResearchReport


class MarkdownOutput:
    """Markdown 格式输出"""

    def generate(self, report: ResearchReport) -> str:
        """生成 Markdown 报告"""
        lines = []

        # 标题
        lines.append(f"# 研究报告：{report.topic}")
        lines.append("")
        lines.append(f"**生成时间：** {report.created_at}")
        lines.append("")

        # 摘要
        lines.append("## 📋 摘要")
        lines.append("")
        lines.append(report.summary)
        lines.append("")

        # 关键发现
        lines.append("## 🔍 关键发现")
        lines.append("")
        for i, finding in enumerate(report.key_findings, 1):
            lines.append(f"{i}. {finding}")
        lines.append("")

        # 热门内容
        lines.append("## 📰 热门内容")
        lines.append("")
        for item in report.top_items:
            title = item.get('title', '无标题')
            url = item.get('url', '')
            score = item.get('score', 0)
            source = item.get('source', 'unknown')
            author = item.get('author', 'unknown')

            lines.append(f"### [{title}]({url})")
            lines.append("")
            lines.append(f"- **来源：** {source}")
            lines.append(f"- **作者：** {author}")
            lines.append(f"- **热度：** {score}")
            if item.get('text'):
                text = item['text'][:200] + "..." if len(item.get('text', '')) > 200 else item['text']
                lines.append(f"- **摘要：** {text}")
            lines.append("")

        # 建议
        lines.append("## 💡 建议")
        lines.append("")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

        # 页脚
        lines.append("---")
        lines.append("")
        lines.append("*由 AI Research Scout 自动生成*")

        return "\n".join(lines)

    def save(self, report: ResearchReport, filepath: str) -> str:
        """保存到文件"""
        content = self.generate(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath