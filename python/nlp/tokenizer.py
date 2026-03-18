import re
from typing import List

class UzbbekTokenizer:
    """Узбекский токенизер для разбора текста"""
    
    STOP_WORDS = {
        'va', 'ili', 'emas', 'bu', 'shuni', 'bilan', 'uchun', 'dan',
        'ni', 'ga', 'ka', 'da', 'jo', 'qo', 'yo', 'bo', 'no', 'temir'
    }
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Разбить текст на токены"""
        text = text.lower().strip()
        
        # Удаляем пунктуацию
        text = re.sub(r'[^\w\s-]', '', text)
        
        # Разбиваем на слова
        tokens = text.split()
        
        # Убираем стоп-слова
        tokens = [t for t in tokens if t and len(t) > 1 and t not in UzbbekTokenizer.STOP_WORDS]
        
        return tokens

if __name__ == '__main__':
    tokenizer = UzbbekTokenizer()
    tests = [
        "Oyniy videoni oching",
        "Youtubni oching va musiqani qoying",
    ]
    for t in tests:
        print(f"{t} → {tokenizer.tokenize(t)}")