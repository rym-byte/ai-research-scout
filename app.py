      
"""AI Research Scout - Web 应用"""
import os
import asyncio
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

from src.collectors import HNCollector, WebCollector
from src.analyzers import ResearchSynthesizer
from src.analyzers.groq_analyzer import analyze_with_groq
from src.outputs import MarkdownOutput

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-research-scout-2026')

# API Token 用于定时任务调用
API_TOKEN = os.environ.get('API_TOKEN', 'sk_live_' + secrets.token_hex(16))

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


async def run_research_with_groq(topic: str, sources: list, limit: int):
    """执行研究 + Groq 深度分析"""
    # 先执行基础研究
    results = await run_research(topic, sources, limit)
    
    # 添加 Groq 深度分析
    if results['items']:
        groq_result = analyze_with_groq(results['items'], topic)
        results['groq_analysis'] = groq_result
    
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


@app.route('/api/trigger', methods=['POST'])
def api_trigger():
    """API: 定时任务触发器（需Token验证）"""
    # Token 验证
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
    
    if token != API_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 执行研究（带 Groq 分析）
    topic = request.json.get('topic', 'AI前沿应用') if request.is_json else 'AI前沿应用'
    sources = ['hn', 'web']
    limit = 15
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_research_with_groq(topic, sources, limit))
    loop.close()
    
    # 保存历史
    history.append({
        'topic': topic,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'count': len(results['items'])
    })
    
    return jsonify({
        'success': True,
        'report': results['report'],
        'groq_analysis': results.get('groq_analysis', {}),
        'items_count': len(results['items']),
        'triggered_at': datetime.now().isoformat()
    })


@app.route('/api/history')
def api_history():
    """API: 获取历史"""
    return jsonify(history[-20:])


@app.route('/api/debug')
def api_debug():
    """API: 调试环境变量"""
    return jsonify({
        "deepseek_key_set": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "groq_key_set": bool(os.environ.get("GROQ_API_KEY")),
        "api_token_set": bool(API_TOKEN),
        "env_keys": [k for k in os.environ.keys() if "DEEPSEEK" in k or "GROQ" in k or "API" in k]
    })


@app.route('/api/token')
def api_token():
    """API: 获取 Token（仅本地开发）"""
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return jsonify({'error': 'Not available in production'}), 403
    return jsonify({'token': API_TOKEN})


if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Railway 需要从环境变量获取端口
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 AI Research Scout Web UI")
    print(f"📍 Running on port: {port}")
    print(f"🔑 API Token: {API_TOKEN}")
    
    # Railway 需要 host='0.0.0.0'
    app.run(host='0.0.0.0', port=port, debug=False)

    
