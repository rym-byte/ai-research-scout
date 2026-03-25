"""AI Research Scout - 主程序"""
import asyncio
import os
from datetime import datetime
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .collectors import HNCollector, WebCollector
from .analyzers import ResearchSynthesizer
from .outputs import MarkdownOutput, JSONOutput

console = Console()


async def collect_data(
    query: str,
    sources: List[str],
    limit: int,
    config: Config
) -> List[dict]:
    """收集数据"""
    all_items = []
    collectors = []

    # 初始化采集器
    if 'hn' in sources:
        collectors.append(('Hacker News', HNCollector()))
    if 'web' in sources:
        collectors.append(('Web', WebCollector()))

    # 收集数据
    for name, collector in collectors:
        try:
            items = await collector.search(query, limit)
            all_items.extend(items)
            console.print(f"  ✓ {name}: 找到 {len(items)} 条")
        except Exception as e:
            console.print(f"  ✗ {name}: 错误 - {e}")
        finally:
            await collector.close()

    return all_items


async def research(
    topic: str,
    sources: List[str] = None,
    limit: int = 10,
    output_format: str = "markdown",
    output_dir: str = "output"
) -> str:
    """执行研究任务"""
    config = Config.load()

    # 默认值
    if sources is None:
        sources = config.default_sources

    # 确保输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 显示标题
    console.print()
    console.print(f"[bold blue]🔍 AI Research Scout[/]")
    console.print(f"[dim]研究主题: {topic}[/]")
    console.print()

    # 收集数据
    console.print("[bold]📡 正在收集数据...[/]")
    items = await collect_data(topic, sources, limit, config)

    if not items:
        console.print("[red]未找到相关信息[/]")
        return None

    # 分析数据
    console.print()
    console.print("[bold]🧠 正在分析...[/]")
    synthesizer = ResearchSynthesizer()
    report = synthesizer.synthesize(items, topic)

    # 生成报告
    console.print("[bold]📝 正在生成报告...[/]")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_{timestamp}"

    if output_format == "json":
        output = JSONOutput()
        filepath = os.path.join(output_dir, f"{filename}.json")
    else:
        output = MarkdownOutput()
        filepath = os.path.join(output_dir, f"{filename}.md")

    output.save(report, filepath)

    # 显示结果
    console.print()
    console.print(f"[green]✓ 报告已生成: {filepath}[/]")
    console.print()

    # 显示摘要
    console.print("[bold]📋 摘要:[/]")
    console.print(f"  {report.summary}")
    console.print()

    # 显示热门内容
    if report.top_items:
        table = Table(title="📰 热门内容")
        table.add_column("标题", style="cyan")
        table.add_column("来源", style="green")
        table.add_column("热度", style="yellow")

        for item in report.top_items[:5]:
            table.add_row(
                item.get('title', '')[:50] + "...",
                item.get('source', ''),
                str(item.get('score', 0))
            )

        console.print(table)

    return filepath


@click.command()
@click.argument('topic')
@click.option('--sources', '-s', default='hn,web', help='数据源 (hn,web)')
@click.option('--limit', '-l', default=10, help='每源采集数量')
@click.option('--output', '-o', default='markdown', help='输出格式 (markdown/json)')
@click.option('--output-dir', '-d', default='output', help='输出目录')
def main(topic: str, sources: str, limit: int, output: str, output_dir: str):
    """AI Research Scout - 跨平台研究工具

    示例:
        python -m src.main "AI Agent 最新趋势"
        python -m src.main "GPT-5" --sources hn --limit 20
        python -m src.main "创业融资" --output json
    """
    sources_list = [s.strip() for s in sources.split(',')]
    asyncio.run(research(topic, sources_list, limit, output, output_dir))


if __name__ == '__main__':
    main()