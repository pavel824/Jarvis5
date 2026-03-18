import json
import re
from typing import List, Dict
from .tokenizer import UzbbekTokenizer
from .lemmatizer import UzbbekLemmatizer

class IntentParser:
    """
    ГЛАВНЫЙ ПАРСЕР - анализирует текст и определяет интенты
    
    Пример:
    "Открой YouTube и найди Eminem" →
    [
        {"action": "app_launch", "category": "app_launch", "params": {"app": "youtube"}},
        {"action": "search", "category": "search", "params": {"query": "eminem"}}
    ]
    """
    
    def __init__(self, vocab_path='nlp/uzbek_vocab.json'):
        self.tokenizer = UzbbekTokenizer()
        self.lemmatizer = UzbbekLemmatizer()
        
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                self.vocab = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Файл {vocab_path} не найден")
            self.vocab = {"commands": {}, "modifiers": {}}
        
        self.word_to_command = self._build_reverse_index()
    
    def _build_reverse_index(self) -> Dict[str, tuple]:
        """Создаём быстрый поиск: слово → (категория, команда)"""
        index = {}
        
        for category, commands in self.vocab.get('commands', {}).items():
            for cmd_name, aliases in commands.items():
                for alias in aliases:
                    index[alias] = (category, cmd_name)
        
        return index
    
    def parse(self, text: str) -> List[Dict]:
        """ГЛАВНЫЙ МЕТОД: текст → список интентов"""
        
        if not text:
            return []
        
        text = text.lower().strip()
        
        # Разделяем по союзам
        sentences = self._split_by_conjunctions(text)
        
        intents = []
        for sentence in sentences:
            intent = self._parse_single_sentence(sentence)
            if intent:
                intents.append(intent)
        
        return intents
    
    def _split_by_conjunctions(self, text: str) -> List[str]:
        """Разделяем текст по союзам (va, keyin, potom)"""
        conjunctions = r'\s+(va|keyin|potom|zatim|damak|yana)\s+'
        sentences = re.split(conjunctions, text)
        return [s for s in sentences if s and not re.match(r'^(va|keyin|potom|zatim)$', s)]
    
    def _parse_single_sentence(self, sentence: str) -> Dict:
        """Парсим одно предложение"""
        sentence = sentence.strip()
        
        tokens = self.tokenizer.tokenize(sentence)
        lemmas = self.lemmatizer.lemmatize_tokens(tokens)
        
        if not lemmas:
            return None
        
        # Ищем КОМАНДУ
        action = None
        category = None
        
        for lemma in lemmas:
            if lemma in self.word_to_command:
                category, action = self.word_to_command[lemma]
                break
        
        if not action:
            return None
        
        intent = {
            'action': action,
            'category': category,
            'params': {}
        }
        
        # Извлекаем параметры
        if category == 'app_launch':
            intent['params']['app'] = action
        
        elif category == 'search':
            query_words = self._extract_query(sentence, action)
            intent['params']['query'] = ' '.join(query_words)
        
        elif category == 'media_control':
            intent['params']['command'] = action
        
        elif category == 'volume_control':
            intent['params']['action'] = action
        
        return intent
    
    def _extract_query(self, sentence: str, action: str) -> List[str]:
        """Извлекаем поисковый запрос из предложения"""
        tokens = self.tokenizer.tokenize(sentence)
        
        # Убираем слово-действие
        action_keywords = []
        for words in self.vocab.get('commands', {}).get('search', {}).values():
            action_keywords.extend(words)
        
        query_words = [t for t in tokens if t not in action_keywords]
        
        return query_words