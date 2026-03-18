import json
import re
from typing import List, Dict
from .tokenizer import UzbbekTokenizer
from .lemmatizer import UzbbekLemmatizer

class IntentParser:
    """Парсер интентов для узбекского"""
    
    def __init__(self, vocab_path='python/nlp/uzbek_vocab.json'):
        self.tokenizer = UzbbekTokenizer()
        self.lemmatizer = UzbbekLemmatizer()
        
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                self.vocab = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Файл {vocab_path} не найден - используем пустой словарь")
            self.vocab = {"commands": {}}
        
        self.word_to_command = self._build_index()
    
    def _build_index(self) -> Dict:
        """Создаём быстрый индекс слово→команда"""
        index = {}
        for category, commands in self.vocab.get('commands', {}).items():
            for cmd_name, aliases in commands.items():
                for alias in aliases:
                    index[alias] = (category, cmd_name)
        return index
    
    def parse(self, text: str) -> List[Dict]:
        """Главный метод: текст → интенты"""
        if not text:
            return []
        
        text = text.lower().strip()
        sentences = self._split_by_conjunctions(text)
        
        intents = []
        for sentence in sentences:
            intent = self._parse_single(sentence)
            if intent:
                intents.append(intent)
        
        return intents
    
    def _split_by_conjunctions(self, text: str) -> List[str]:
        """Разделяем по союзам"""
        conjunctions = r'\s+(va|keyin|potom|zatim)\s+'
        sentences = re.split(conjunctions, text)
        return [s for s in sentences if s and not re.match(r'^(va|keyin|potom|zatim)$', s)]
    
    def _parse_single(self, sentence: str) -> Dict:
        """Парсим одно предложение"""
        sentence = sentence.strip()
        tokens = self.tokenizer.tokenize(sentence)
        lemmas = self.lemmatizer.lemmatize_tokens(tokens)
        
        if not lemmas:
            return None
        
        # Ищем команду
        for lemma in lemmas:
            if lemma in self.word_to_command:
                category, action = self.word_to_command[lemma]
                return {
                    'action': action,
                    'category': category,
                    'params': {}
                }
        
        return None