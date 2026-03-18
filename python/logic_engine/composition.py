from typing import List, Dict
import json

class CommandComposer:
    """Берёт интенты и создаёт ЦЕПОЧКУ КОМАНД с зависимостями"""
    
    def __init__(self, graph_path='knowledge_graph/graph_data.json'):
        try:
            with open(graph_path, 'r', encoding='utf-8') as f:
                self.graph = json.load(f)
        except:
            self.graph = {}
    
    def compose(self, intents: List[Dict]) -> List[Dict]:
        """Составляет цепочку команд из интентов"""
        
        if not intents:
            return []
        
        # Сортируем по приоритету
        sorted_intents = self._sort_by_priority(intents)
        
        commands = []
        for i, intent in enumerate(sorted_intents):
            cmd = self._intent_to_command(intent, i + 1)
            if cmd:
                commands.append(cmd)
        
        # Добавляем зависимости
        commands = self._add_dependencies(commands)
        
        return commands
    
    def _sort_by_priority(self, intents: List[Dict]) -> List[Dict]:
        """Приоритет: app_launch → search → play → volume"""
        priority = {
            'app_launch': 10,
            'search': 5,
            'play': 4,
            'media_control': 3,
            'volume_control': 1,
        }
        
        return sorted(
            intents,
            key=lambda x: priority.get(x.get('action'), 0),
            reverse=True
        )
    
    def _intent_to_command(self, intent: Dict, cmd_id: int) -> Dict:
        """Преобразуем интент в команду"""
        return {
            'id': cmd_id,
            'type': intent.get('category'),
            'action': intent.get('action'),
            'params': intent.get('params', {}),
            'wait_ms': 2000 if intent.get('category') == 'app_launch' else 500
        }
    
    def _add_dependencies(self, commands: List[Dict]) -> List[Dict]:
        """Добавляем зависимости между командами"""
        for i, cmd in enumerate(commands):
            if i > 0 and commands[i-1]['type'] == 'app_launch':
                cmd['depends_on'] = commands[i-1]['id']
        
        return commands