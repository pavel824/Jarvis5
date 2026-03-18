from flask import Flask, request, jsonify
import logging
import json
import sys
import os

# Подавляем вывод werkzeug
import warnings
warnings.filterwarnings('ignore')
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Инициализируем (заглушки для примера)
class IntentParser:
    def parse(self, text):
        # Простой парсер - ищет ключевые слова
        text_lower = text.lower()
        intents = []
        
        if any(word in text_lower for word in ['салом', 'привет', 'здравствуй']):
            intents.append('greeting')
        if any(word in text_lower for word in ['кутмоқ', 'открыть', 'запустить']):
            intents.append('open_app')
        if any(word in text_lower for word in ['ёпиш', 'напиши', 'написать']):
            intents.append('write_text')
        if any(word in text_lower for word in ['чиқ', 'выход', 'стоп']):
            intents.append('exit')
            
        return intents if intents else ['unknown']

class CommandComposer:
    def compose(self, intents):
        commands = []
        for intent in intents:
            if intent == 'greeting':
                commands.append({'action': 'say', 'text': 'Саломатлик! 👋'})
            elif intent == 'open_app':
                commands.append({'action': 'open', 'app': 'terminal'})
            elif intent == 'write_text':
                commands.append({'action': 'type', 'text': 'текст'})
            elif intent == 'exit':
                commands.append({'action': 'exit'})
            else:
                commands.append({'action': 'log', 'text': 'Не понял команду'})
        return commands

class CommandExecutor:
    def execute(self, commands):
        results = []
        for cmd in commands:
            action = cmd.get('action')
            if action == 'say':
                print(f"🤖 JARVIS: {cmd.get('text', '')}")
                results.append(f"Сказал: {cmd.get('text')}")
            elif action == 'log':
                print(f"⚠️  {cmd.get('text')}")
                results.append(cmd.get('text'))
            elif action == 'exit':
                results.append('Завершение...')
            else:
                results.append(f'Выполнена команда: {action}')
        return results

# Инициализируем движки
intent_parser = IntentParser()
composer = CommandComposer()
executor = CommandExecutor()

@app.route('/process_speech', methods=['POST'])
def process_speech():
    """
    Получает текст от C++ STT сервера
    Обрабатывает через NLP, компонует команды, выполняет
    """
    try:
        data = request.json
        speech_text = data.get('text', '').strip()
        
        if not speech_text:
            return jsonify({'error': 'Empty text'}), 400
        
        print(f"\n📝 Полученный текст: {speech_text}")
        
        # 1️⃣ АНАЛИЗИРУЕМ ИНТЕНТ
        intents = intent_parser.parse(speech_text)
        print(f"🧠 Интенты: {intents}")
        
        # 2️⃣ КОМПОНУЕМ КОМАНДЫ
        command_chain = composer.compose(intents)
        print(f"⛓️  Команды: {[c.get('action') for c in command_chain]}")
        
        # 3️⃣ ВЫПОЛНЯЕМ КОМАНДЫ
        results = executor.execute(command_chain)
        print(f"✅ Результаты: {results}")
        print("════════════════════════════════════════\n")
        
        return jsonify({
            'success': True,
            'input': speech_text,
            'intents': intents,
            'commands': command_chain,
            'results': results
        })
        
    except Exception as e:
        print(f"❌ Ошибка обработки: {str(e)}\n")
        logger.error(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0'})

if __name__ == '__main__':
    print("════════════════════════════════════════")
    print("🎤 JARVIS 5 - Python NLP Engine")
    print("🚀 Запущен на localhost:5000")
    print("⏳ Ожидание текста от C++ STT сервера...")
    print("════════════════════════════════════════\n")
    
    # Flask слушает на 5000, C++ слушает на 8080
    app.run(host='localhost', port=5000, debug=False)