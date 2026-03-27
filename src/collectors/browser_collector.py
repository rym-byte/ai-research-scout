"""浏览器采集器基类 - 使用 agent-browser 进行网页采集"""
import asyncio
import json
import subprocess
import shutil
from typing import List, Optional
from datetime import datetime
from . import BaseCollector, SourceItem


# 检查 agent-browser 是否可用
AGENT_BROWSER_AVAILABLE = shutil.which('agent-browser') is not None


class BrowserCollector(BaseCollector):
    """基于 agent-browser 的网页采集器基类"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.session_name = self.platform_name
        
    def _check_agent_browser(self) -> bool:
        """检查 agent-browser 是否可用"""
        if not AGENT_BROWSER_AVAILABLE:
            print(f"Warning: agent-browser not available for {self.platform_name}")
            return False
        return True
        
    async def _browser_open(self, url: str) -> bool:
        """使用 agent-browser 打开页面"""
        if not self._check_agent_browser():
            return False
        try:
            result = subprocess.run(
                ['agent-browser', '--session', self.session_name, 'open', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Browser open error: {e}")
            return False
    
    async def _browser_snapshot(self, interactive: bool = True) -> Optional[dict]:
        """获取页面快照"""
        try:
            cmd = ['agent-browser', '--session', self.session_name, 'snapshot']
            if interactive:
                cmd.extend(['-i', '--json'])
            else:
                cmd.append('--json')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"Browser snapshot error: {e}")
            return None
    
    async def _browser_get_text(self, ref: str) -> str:
        """获取元素文本"""
        try:
            result = subprocess.run(
                ['agent-browser', '--session', self.session_name, 'get', 'text', ref, '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('data', {}).get('text', '')
            return ''
        except Exception as e:
            print(f"Browser get text error: {e}")
            return ''
    
    async def _browser_click(self, ref: str) -> bool:
        """点击元素"""
        try:
            result = subprocess.run(
                ['agent-browser', '--session', self.session_name, 'click', ref],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Browser click error: {e}")
            return False
    
    async def _browser_type(self, ref: str, text: str) -> bool:
        """输入文本"""
        try:
            result = subprocess.run(
                ['agent-browser', '--session', self.session_name, 'fill', ref, text],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Browser type error: {e}")
            return False
    
    async def _browser_press(self, key: str) -> bool:
        """按下按键"""
        try:
            result = subprocess.run(
                ['agent-browser', '--session', self.session_name, 'press', key],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Browser press error: {e}")
            return False
    
    async def _browser_wait(self, milliseconds: int = 1000) -> bool:
        """等待"""
        try:
            result = subprocess.run(
                ['agent-browser', '--session', self.session_name, 'wait', str(milliseconds)],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Browser wait error: {e}")
            return False
    
    async def close(self):
        """关闭浏览器会话"""
        try:
            subprocess.run(
                ['agent-browser', '--session', self.session_name, 'close'],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            print(f"Browser close error: {e}")
