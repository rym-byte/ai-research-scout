"""AI Research Scout - Web 应用"""
import os
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

from src.collectors import HNCollector, WebCollector
from src.analyzers import ResearchSynthesizer
from src.outputs import MarkdownOutput

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-research-scout-2026'

# 存储历史记录
history = []


async def run_research(topic: str, sources: list, limit: int):
    """执行研究"""
    all_items = []
    collectors = []

    if 'hn' in sources:
        collectors.append(('Hacker News', HNCollector()))
    if 'web' in sources:
        collectors.append(('Web', WebCollector()))

    results = {'sources': {}, 'items': [], 'report': None}

    for name, collector in collectors:
        try:
            items = await collector.search(topic, limit)
            all_items.extend(items)
            results['sources'][name] = len(items)
        except Exception as e:
            results['sources'][name] = f"错误: {str(e)}"
        finally:
            await collector.close()

    # 分析
    synthesizer = ResearchSynthesizer()
    report = synthesizer.synthesize(all_items, topic)

    results['items'] = all_items
    results['report'] = {
        'topic': report.topic,
        'summary': report.summary,
        'key_findings': report.key_findings,
        'recommendations': report.recommendations,
        'created_at': report.created_at
    }

    return results


@app.route('/')
def index():
    """首页"""
    return render_template('index.html', history=history[-10:])


@app.route('/api/research', methods=['POST'])
def api_research():
    """API: 执行研究"""
    data = request.get_json()
    topic = data.get('topic', '').strip()
    sources = data.get('sources', ['hn', 'web'])
    limit = int(data.get('limit', 10))

    if not topic:
        return jsonify({'error': '请输入研究主题'}), 400

    # 执行研究
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_research(topic, sources, limit))
    loop.close()

    # 保存历史
    history.append({
        'topic': topic,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'count': len(results['items'])
    })

    return jsonify(results)


@app.route('/api/history')
def api_history():
    """API: 获取历史"""
    return jsonify(history[-20:])


if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Railway 需要从环境变量获取端口
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 AI Research Scout Web UI")
    print(f"📍 Running on port: {port}")
    
    # Railway 需要 host='0.0.0.0'
    app.run(host='0.0.0.0', port=port, debug=False)
