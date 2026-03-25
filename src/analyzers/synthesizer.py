"""研究报告合成器"""
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ResearchReport:
    """研究报告"""
    topic: str
    summary: str
    key_findings: List[str]
    top_items: List[Dict[str, Any]]
    recommendations: List[str]
    created_at: str


class ResearchSynthesizer:
    """研究报告合成器（规则引擎版本）"""

    def synthesize(self, sources: List[Dict[str, Any]], topic: str) -> ResearchReport:
        """合成研究报告"""
        if not sources:
            return ResearchReport(
                topic=topic,
                summary=f"未找到关于「{topic}」的相关信息。",
                key_findings=[],
                top_items=[],
                recommendations=["尝试更换关键词搜索"],
                created_at=datetime.now().isoformat()
            )

        # 按分数排序
        sorted_sources = sorted(sources, key=lambda x: x.get('score', 0), reverse=True)

        # 提取关键发现
        key_findings = self._extract_key_findings(sorted_sources)

        # 生成摘要
        summary = self._generate_summary(topic, sorted_sources)

        # 生成建议
        recommendations = self._generate_recommendations(topic, sorted_sources)

        # 提取热门项目
        top_items = sorted_sources[:5]

        return ResearchReport(
            topic=topic,
            summary=summary,
            key_findings=key_findings,
            top_items=top_items,
            recommendations=recommendations,
            created_at=datetime.now().isoformat()
        )

    def _extract_key_findings(self, sources: List[Dict]) -> List[str]:
        """提取关键发现"""
        findings = []

        # 统计来源分布
        source_counts = {}
        for item in sources:
            src = item.get('source', 'unknown')
            source_counts[src] = source_counts.get(src, 0) + 1

        findings.append(f"共收集 {len(sources)} 条相关信息")
        findings.append(f"来源分布: {', '.join(f'{k}({v})' for k, v in source_counts.items())}")

        # 提取高分项目
        high_score = [s for s in sources if s.get('score', 0) > 100]
        if high_score:
            findings.append(f"发现 {len(high_score)} 条高热度内容（得分>100）")

        return findings

    def _generate_summary(self, topic: str, sources: List[Dict]) -> str:
        """生成摘要"""
        if not sources:
            return f"未找到关于「{topic}」的相关信息。"

        top_titles = [s.get('title', '') for s in sources[:3] if s.get('title')]

        summary = f"关于「{topic}」的研究报告。"
        summary += f"我们收集了 {len(sources)} 条相关信息。"

        if top_titles:
            summary += f"热门讨论包括：{'; '.join(top_titles[:2])} 等。"

        return summary

    def _generate_recommendations(self, topic: str, sources: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于数据量的建议
        if len(sources) < 5:
            recommendations.append("数据量较少，建议扩大搜索范围或更换关键词")
        elif len(sources) > 20:
            recommendations.append("数据量充足，可以深入分析特定方向")

        # 基于热度的建议
        high_score = [s for s in sources if s.get('score', 0) > 100]
        if high_score:
            recommendations.append(f"关注 {len(high_score)} 条高热度内容，这些是当前讨论焦点")

        # 默认建议
        if not recommendations:
            recommendations.append("建议进一步追踪相关话题的发展动态")

        return recommendations