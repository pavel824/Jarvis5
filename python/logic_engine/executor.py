import subprocess
import time
import os
from typing import List, Dict
import logging
from commands.automation import AutomationCommands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandExecutor:
    """Выполняет цепочку команд на Linux"""
    
    APP_COMMANDS = {
        'youtube': 'xdg-open https://youtube.com',
        'telegram': 'telegram-desktop',
        'discord': 'discord',
        'code': 'code',
        'chrome': 'google-chrome',
        'firefox': 'firefox',
        'nautilus': 'nautilus',
        'terminal': 'gnome-terminal',
        'spotify': 'spotify',
        'vlc': 'vlc',
    }
    
    def __init__(self):
        self.automation = AutomationCommands()
    
    def execute(self, command_chain: List[Dict]) -> List[Dict]:
        """Выполняем цепочку команд"""
        results = []
        
        for cmd in command_chain:
            logger.info(f"▶️  Command {cmd['id']}: {cmd['action']}")
            
            # Если есть зависимость - ждём
            if cmd.get('depends_on'):
                time.sleep(cmd.get('wait_ms', 2000) / 1000)
            
            # Выполняем
            result = self._execute_single(cmd)
            results.append(result)
        
        return results
    
    def _execute_single(self, cmd: Dict) -> Dict:
        """Выполняем одну команду"""
        try:
            cmd_type = cmd['type']
            action = cmd['action']
            params = cmd.get('params', {})
            
            if cmd_type == 'app_launch':
                return self._launch_app(action)
            
            elif cmd_type == 'search':
                return self._perform_search(action, params)
            
            elif cmd_type == 'media_control':
                return self._media_control(action)
            
            elif cmd_type == 'volume_control':
                return self._volume_control(action)
            
            # НОВЫЕ КОМАНДЫ АВТОМАТИЗАЦИИ
            elif action == 'night_mode':
                return self.automation.night_mode(params)
            
            elif action == 'morning_mode':
                return self.automation.morning_mode(params)
            
            elif action == 'discord_send_message':
                return self.automation.discord_send_message(params)
            
            elif action == 'set_timer':
                return self.automation.set_timer(params)
            
            elif action == 'open_and_search':
                return self.automation.open_and_search(params)
            
            else:
                return {'success': False, 'error': f'Unknown: {cmd_type}'}
        
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _launch_app(self, app_name: str) -> Dict:
        """Открываем приложение"""
        app_name = app_name.lower()
        
        if app_name not in self.APP_COMMANDS:
            return {'success': False, 'error': f'App not found: {app_name}'}
        
        cmd = self.APP_COMMANDS[app_name]
        
        try:
            subprocess.Popen(cmd, shell=True)
            logger.info(f"✅ Launched: {app_name}")
            return {'success': True, 'app': app_name}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _perform_search(self, search_engine: str, params: Dict) -> Dict:
        """Выполняем поиск"""
        query = params.get('query', '').strip()
        
        if not query:
            return {'success': False, 'error': 'Empty query'}
        
        try:
            time.sleep(1)
            os.system("xdotool key ctrl+f")
            time.sleep(0.5)
            os.system(f'xdotool type "{query}"')
            time.sleep(0.3)
            os.system("xdotool key Return")
            
            logger.info(f"🔍 Searched: {query}")
            return {'success': True, 'query': query}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _media_control(self, action: str) -> Dict:
        """Управление медиа"""
        commands = {
            'play': 'playerctl play',
            'pause': 'playerctl pause',
            'next': 'playerctl next',
            'previous': 'playerctl previous',
            'stop': 'playerctl stop',
        }
        
        if action not in commands:
            return {'success': False, 'error': f'Unknown: {action}'}
        
        try:
            subprocess.run(commands[action], shell=True)
            return {'success': True, 'action': action}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _volume_control(self, action: str) -> Dict:
        """Управление громкостью"""
        
        if action == 'increase':
            os.system("amixer sset Master 5%+")
        elif action == 'decrease':
            os.system("amixer sset Master 5%-")
        elif action == 'mute':
            os.system("amixer sset Master toggle")
        
        return {'success': True, 'action': action}