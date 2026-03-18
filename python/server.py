from flask import Flask, request, jsonify
from nlp.intent_parser import IntentParser
from logic_engine.composition import CommandComposer
from logic_engine.executor import CommandExecutor
import logging
import json
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем движки
intent_parser = IntentParser()
composer = CommandComposer()
executor = CommandExecutor()

@app.route('/process_speech', methods=['POST'])
def process_speech():
    """
    Получает текст от C++ STT сервера на 8080
    Обрабатывает через NLP, компонует команды, выполняет
    """
    try:
        data = request.json
        speech_text = data.get('text', '').strip()
        language = data.get('language', 'uz')
        
        if not speech_text:
            return jsonify({'error': 'Empty text'}), 400
        
        logger.info(f"📝 Input: {speech_text}")
        
        # 1️⃣ АНАЛИЗИРУЕМ ИНТЕНТ
        intents = intent_parser.parse(speech_text)
        logger.info(f"🧠 Intents: {intents}")
        
        # 2️⃣ КОМПОНУЕМ КОМАНДЫ
        command_chain = composer.compose(intents)
        logger.info(f"⛓️  Command chain: {command_chain}")
        
        # 3️⃣ ВЫПОЛНЯЕМ КОМАНДЫ
        results = executor.execute(command_chain)
        logger.info(f"✅ Results: {results}")
        
        return jsonify({
            'success': True,
            'input': speech_text,
            'intents': intents,
            'commands': command_chain,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0'})

if __name__ == '__main__':
    print("🎤 JARVIS 5 - Python NLP Engine")
    print("🚀 Запуск на localhost:5000")
    print("⏳ Ожидание текста от C++ STT сервера...")
    app.run(host='localhost', port=8080, debug=True)