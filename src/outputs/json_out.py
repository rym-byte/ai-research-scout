"""JSON 报告输出"""
import json
from ..analyzers.synthesizer import ResearchReport


class JSONOutput:
    """JSON 格式输出"""

    def generate(self, report: ResearchReport) -> str:
        """生成 JSON 报告"""
        data = {
            'topic': report.topic,
            'summary': report.summary,
            'key_findings': report.key_findings,
            'top_items': report.top_items,
            'recommendations': report.recommendations,
            'created_at': report.created_at
        }
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)

    def save(self, report: ResearchReport, filepath: str) -> str:
        """保存到文件"""
        content = self.generate(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath