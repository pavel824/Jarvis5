import time
import subprocess
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AutomationCommands:
    """
    Сложные команды которые комбинируют несколько действий
    
    Примеры:
    - "Зайди в Discord и найди Дженнифер и напиши ей привет"
    - "Включи ночной режим" (яркость + музыка)
    - "Установи таймер на 30 минут"
    """
    
    def __init__(self):
        self.current_window = None
    
    def discord_send_message(self, params: Dict) -> Dict:
        """
        Сложная команда: открыть Discord → найти пользователя → отправить сообщение
        
        Пример:
        params = {
            "username": "jennifer",
            "message": "Сегодня я не смогу прийти"
        }
        """
        try:
            username = params.get('username', '').strip()
            message = params.get('message', '').strip()
            
            if not username or not message:
                return {'success': False, 'error': 'Missing username or message'}
            
            logger.info(f"📱 Discord: найти {username} и отправить сообщение")
            
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
            
            # 5. Кликаем в текстовое поле
            os.system("xdotool key ctrl+End")
            time.sleep(0.5)
            
            # 6. Вводим сообщение
            os.system(f'xdotool type "{message}"')
            time.sleep(0.5)
            
            # 7. Отправляем (Shift+Enter или Ctrl+Enter)
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
        3. Устанавливаем теплый фильтр свет
        """
        try:
            logger.info("🌙 Включаю ночной режим...")
            
            # Получаем текущую яркость
            result = os.popen('brightnessctl get').read().strip()
            current_brightness = int(result) if result.isdigit() else 100
            
            target_brightness = 30
            
            # Плавно снижаем яркость (каждые 0.1 сек на 5%)
            while current_brightness > target_brightness:
                current_brightness -= 5
                os.system(f'brightnessctl set {current_brightness}%')
                time.sleep(0.1)
            
            logger.info(f"✅ Яркость снижена до {target_brightness}%")
            
            # Включаем спокойную музыку в Spotify
            time.sleep(1)
            subprocess.Popen('spotify', shell=True)
            time.sleep(2)
            
            # Ищем плейлист "спокойная музыка" или "релаксация"
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
                'music': 'chill playlist'
            }
        
        except Exception as e:
            logger.error(f"❌ Night mode error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def morning_mode(self, params: Dict) -> Dict:
        """
        Утренний режим: повысить яркость, энергичная музыка
        """
        try:
            logger.info("☀️  Включаю утренний режим...")
            
            target_brightness = 100
            
            # Плавно повышаем яркость
            result = os.popen('brightnessctl get').read().strip()
            current_brightness = int(result) if result.isdigit() else 30
            
            while current_brightness < target_brightness:
                current_brightness += 5
                os.system(f'brightnessctl set {current_brightness}%')
                time.sleep(0.1)
            
            logger.info(f"✅ Яркость повышена до {target_brightness}%")
            
            # Включаем энергичную музыку
            time.sleep(1)
            subprocess.Popen('spotify', shell=True)
            time.sleep(2)
            
            os.system("xdotool key ctrl+f")
            time.sleep(0.5)
            os.system('xdotool type "motivation"')
            time.sleep(1)
            os.system("xdotool key Return")
            
            logger.info("✅ Энергичная музыка включена")
            
            return {
                'success': True,
                'action': 'morning_mode',
                'brightness': target_brightness,
                'music': 'motivation playlist'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_timer(self, params: Dict) -> Dict:
        """
        Установить таймер через командную строку
        
        params: {"minutes": 30}
        """
        try:
            minutes = params.get('minutes', 5)
            
            logger.info(f"⏲️  Таймер на {minutes} минут")
            
            # Используем встроенные инструменты Linux
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
            
            logger.info(f"🔍 Открываю {app} и ищу '{query}'")
            
            # Открываем приложение
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