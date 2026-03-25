# AI Research Scout

一个跨平台AI研究工具，自动收集、分析、合成研究报告。

## 在线演示

部署后会有一个免费 URL

## 快速部署到 Railway

### 方法一：Railway CLI（推荐）

```bash
# 1. 登录 Railway
railway login

# 2. 初始化项目
railway init

# 3. 部署
railway up

# 4. 查看部署 URL
railway domain
```

### 方法二：GitHub 连接

1. 将代码推送到 GitHub
2. 访问 railway.app
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择仓库，自动部署

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 Web 界面
python app.py

# 或命令行使用
python -m src.main "研究主题"
```

## 功能特性

- ✅ Hacker News 数据采集
- ✅ Web 搜索
- ✅ AI 分析
- ✅ Markdown/JSON 报告输出
- ✅ Web UI 界面

## 许可证

MIT