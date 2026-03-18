import subprocess
import time
import os
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandExecutor:
    """Выполняет команды на Linux - ПОЛНАЯ ВЕРСИЯ"""
    
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
            logger.info(f"▶️  Команда {cmd['id']}: {cmd['action']}")
            
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
            
            # ОСНОВНЫЕ КОМАНДЫ
            if cmd_type == 'app_launch':
                return self._launch_app(action)
            
            elif cmd_type == 'search':
                return self._perform_search(action, params)
            
            elif cmd_type == 'media_control':
                return self._media_control(action)
            
            elif cmd_type == 'volume_control':
                return self._volume_control(action)
            
            elif cmd_type == 'system':
                return self._system_command(action, params)
            
            # СЛОЖНЫЕ КОМАНДЫ АВТОМАТИЗАЦИИ
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
            
            elif action == 'compose_commands':
                return self.automation.compose_commands(params)
            
            else:
                return {'success': False, 'error': f'Unknown: {cmd_type}'}
        
        except Exception as e:
            logger.error(f"❌ Ошибка: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _launch_app(self, app_name: str) -> Dict:
        """Открываем приложение"""
        app_name = app_name.lower()
        
        if app_name not in self.APP_COMMANDS:
            return {'success': False, 'error': f'App not found: {app_name}'}
        
        try:
            subprocess.Popen(self.APP_COMMANDS[app_name], shell=True)
            logger.info(f"✅ Запущено: {app_name}")
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
            
            logger.info(f"🔍 Поиск: {query}")
            return {'success': True, 'query': query}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _media_control(self, action: str) -> Dict:
        """Управление медиа (play, pause, next, previous)"""
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
            logger.info(f"🎵 Медиа: {action}")
            return {'success': True, 'action': action}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _volume_control(self, action: str) -> Dict:
        """Управление громкостью"""
        try:
            if action == 'increase':
                os.system("amixer sset Master 5%+")
            elif action == 'decrease':
                os.system("amixer sset Master 5%-")
            elif action == 'mute':
                os.system("amixer sset Master toggle")
            
            logger.info(f"🔊 Громкость: {action}")
            return {'success': True, 'action': action}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _system_command(self, action: str, params: Dict) -> Dict:
        """Системные команды (яркость, WiFi и т.д.)"""
        try:
            if action == 'brightness':
                level = params.get('level', 50)
                os.system(f'brightnessctl set {level}%')
                return {'success': True, 'brightness': level}
            
            elif action == 'wifi':
                toggle = params.get('toggle', 'on')
                os.system(f'nmcli radio wifi {toggle}')
                return {'success': True, 'wifi': toggle}
            
            return {'success': False, 'error': f'Unknown system action: {action}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AutomationCommands:
    """СЛОЖНЫЕ КОМАНДЫ - автоматизация"""
    
    def discord_send_message(self, params: Dict) -> Dict:
        """
        Зайти в Discord → найти пользователя → отправить сообщение
        
        params: {
            "username": "jennifer",
            "message": "Привет, как дела?"
        }
        """
        try:
            username = params.get('username', '').strip()
            message = params.get('message', '').strip()
            
            if not username or not message:
                return {'success': False, 'error': 'Missing username or message'}
            
            logger.info(f"📱 Discord: {username}")
            
            # 1. Открываем Discord
            subprocess.Popen('discord', shell=True)
            time.sleep(3)
            
            # 2. Нажимаем Ctrl+K (поиск)
            os.system("xdotool key ctrl+k")
            time.sleep(0.5)
            
            # 3. Вводим имя пользователя
            os.system(f'xdotool type "{username}"')
            time.sleep(1)
            
            # 4. Нажимаем Enter
            os.system("xdotool key Return")
            time.sleep(1)
            
            # 5. Вводим сообщение
            os.system(f'xdotool type "{message}"')
            time.sleep(0.5)
            
            # 6. Отправляем
            os.system("xdotool key Return")
            
            logger.info(f"✅ Сообщение отправлено {username}")
            return {
                'success': True,
                'action': 'discord_send_message',
                'username': username,
                'message': message
            }
        
        except Exception as e:
            logger.error(f"❌ Discord error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def night_mode(self, params: Dict) -> Dict:
        """
        Ночной режим:
        1. Плавно снижаем яркость (100% → 30%)
        2. Включаем спокойную музыку
        3. Теплый свет (если есть)
        """
        try:
            logger.info("🌙 Ночной режим...")
            
            # Получаем текущую яркость
            result = os.popen('brightnessctl get').read().strip()
            current_brightness = int(result) if result.isdigit() else 100
            
            target_brightness = 30
            
            # Плавно снижаем яркость
            while current_brightness > target_brightness:
                current_brightness -= 5
                os.system(f'brightnessctl set {current_brightness}%')
                time.sleep(0.1)
            
            logger.info(f"✅ Яркость: {target_brightness}%")
            
            # Включаем спокойную музыку
            time.sleep(1)
            subprocess.Popen('spotify', shell=True)
            time.sleep(2)
            
            # Ищем плейлист "chill"
            os.system("xdotool key ctrl+f")
            time.sleep(0.5)
            os.system('xdotool type "chill"')
            time.sleep(1)
            os.system("xdotool key Return")
            
            logger.info("✅ Спокойная музыка включена")
            
            return {
                'success': True,
                'action': 'night_mode',
                'brightness': target_brightness,
                'music': 'chill'
            }
        
        except Exception as e:
            logger.error(f"❌ Night mode error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def morning_mode(self, params: Dict) -> Dict:
        """
        Утренний режим:
        1. Плавно повышаем яркость (30% → 100%)
        2. Энергичная музыка
        """
        try:
            logger.info("☀️  Утренний режим...")
            
            result = os.popen('brightnessctl get').read().strip()
            current_brightness = int(result) if result.isdigit() else 30
            target_brightness = 100
            
            # Плавно повышаем яркость
            while current_brightness < target_brightness:
                current_brightness += 5
                os.system(f'brightnessctl set {current_brightness}%')
                time.sleep(0.1)
            
            logger.info(f"✅ Яркость: {target_brightness}%")
            
            # Энергичная музыка
            time.sleep(1)
            subprocess.Popen('spotify', shell=True)
            time.sleep(2)
            
            os.system("xdotool key ctrl+f")
            time.sleep(0.5)
            os.system('xdotool type "motivation"')
            time.sleep(1)
            os.system("xdotool key Return")
            
            logger.info("✅ Мотивирующая музыка включена")
            
            return {
                'success': True,
                'action': 'morning_mode',
                'brightness': target_brightness,
                'music': 'motivation'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_timer(self, params: Dict) -> Dict:
        """Установить таймер"""
        try:
            minutes = params.get('minutes', 5)
            logger.info(f"⏲️  Таймер на {minutes} минут")
            
            # Используем встроенные инструменты
            command = f'at now + {minutes} minutes <<< "notify-send \'⏰ Таймер\' \'Время вышло!\'"'
            os.system(command)
            
            return {
                'success': True,
                'action': 'set_timer',
                'minutes': minutes
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def open_and_search(self, params: Dict) -> Dict:
        """
        Открыть приложение И выполнить поиск
        
        params: {
            "app": "youtube",
            "query": "eminem"
        }
        """
        try:
            app = params.get('app', '').lower()
            query = params.get('query', '').strip()
            
            if not app or not query:
                return {'success': False, 'error': 'Missing app or query'}
            
            logger.info(f"🔍 {app}: {query}")
            
            app_commands = {
                'youtube': 'xdg-open https://youtube.com',
                'google': 'xdg-open https://google.com',
                'wikipedia': 'xdg-open https://wikipedia.org',
            }
            
            if app in app_commands:
                subprocess.Popen(app_commands[app], shell=True)
                time.sleep(3)
            
            # Выполняем поиск
            os.system("xdotool key ctrl+f")
            time.sleep(0.5)
            os.system(f'xdotool type "{query}"')
            time.sleep(0.3)
            os.system("xdotool key Return")
            
            logger.info(f"✅ Поиск '{query}' в {app}")
            
            return {
                'success': True,
                'action': 'open_and_search',
                'app': app,
                'query': query
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def compose_commands(self, command_list: List[Dict]) -> Dict:
        """
        Выполнить последовательность команд с задержками
        
        Пример:
        [
            {"action": "app_launch", "params": {"app": "discord"}},
            {"action": "wait", "params": {"seconds": 2}},
            {"action": "type", "params": {"text": "привет"}},
            {"action": "press", "params": {"key": "Return"}}
        ]
        """
        try:
            logger.info(f"⛓️  Выполняю {len(command_list)} команд...")
            
            for cmd in command_list:
                action = cmd.get('action')
                params = cmd.get('params', {})
                
                if action == 'wait':
                    seconds = params.get('seconds', 1)
                    time.sleep(seconds)
                
                elif action == 'type':
                    text = params.get('text', '')
                    os.system(f'xdotool type "{text}"')
                
                elif action == 'press':
                    key = params.get('key', 'Return')
                    os.system(f'xdotool key {key}')
                
                elif action == 'app_launch':
                    app = params.get('app', '')
                    if app == 'discord':
                        subprocess.Popen('discord', shell=True)
                
                logger.info(f"  ✓ {action}")
            
            return {
                'success': True,
                'action': 'compose_commands',
                'count': len(command_list)
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}