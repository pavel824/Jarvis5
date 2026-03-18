from typing import List

class UzbbekLemmatizer:
    """Лемматизер для узбекского языка"""
    
    LEMMA_RULES = {
        'oching': 'och',
        'ochish': 'och',
        'ochayin': 'och',
        'qoying': 'qoy',
        'qoyish': 'qoy',
        'o\'chirding': 'o\'chir',
    }
    
    def lemmatize(self, word: str) -> str:
        """Привести слово к базовой форме"""
        word = word.lower()
        
        if word in self.LEMMA_RULES:
            return self.LEMMA_RULES[word]
        
        # Удаляем суффиксы
        if word.endswith('shi'):
            return word[:-2]
        if word.endswith('ni'):
            return word[:-2]
        if word.endswith('ga'):
            return word[:-2]
        
        return word
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Лемматизировать список токенов"""
        return [self.lemmatize(token) for token in tokens]