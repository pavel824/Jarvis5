#include "recognizer.h"
#include <stdexcept>
#include <vector>
#include <algorithm>
#include <cstring>
#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fstream>
#include <sstream>
#include <json/json.h>

Recognizer::Recognizer(const std::string& api_key)
{
    // Для Aisha AI нам нужен только API ключ
    if (api_key.empty()) {
        throw std::runtime_error("API ключ Aisha не предоставлен");
    }
    // Сохраняем API ключ в приватное поле (добавь в .h файл)
    this->api_key = api_key;
    std::cout << "✅ Aisha AI Recognizer инициализирован\n";
}

Recognizer::~Recognizer()
{
    // Для Aisha нечего очищать
}

void Recognizer::reset() 
{ 
    // Для Aisha нечего сбрасывать
}

// Сохранить аудио в WAV формат
void Recognizer::saveAudioToWav(const std::vector<float>& audio, const std::string& filename)
{
    std::ofstream file(filename, std::ios::binary);
    if (!file) return;

    int sample_rate = 16000;
    int channels = 1;
    int bits_per_sample = 16;
    int byte_rate = sample_rate * channels * bits_per_sample / 8;
    int block_align = channels * bits_per_sample / 8;
    int data_size = audio.size() * 2;

    // WAV заголовок
    file.write("RIFF", 4);
    int file_size = 36 + data_size;
    file.write((char*)&file_size, 4);
    file.write("WAVE", 4);
    
    file.write("fmt ", 4);
    int fmt_size = 16;
    file.write((char*)&fmt_size, 4);
    short audio_format = 1;
    file.write((char*)&audio_format, 2);
    file.write((char*)&channels, 2);
    file.write((char*)&sample_rate, 4);
    file.write((char*)&byte_rate, 4);
    file.write((char*)&block_align, 2);
    file.write((char*)&bits_per_sample, 2);
    
    file.write("data", 4);
    file.write((char*)&data_size, 4);

    // Конвертируем float [-1.0, 1.0] в int16
    for (float sample : audio) {
        float clamped = std::clamp(sample, -1.0f, 1.0f);
        short pcm = static_cast<short>(clamped * 32767.0f);
        file.write((char*)&pcm, 2);
    }

    file.close();
}

// Отправить на Aisha AI через Python сервис
std::string Recognizer::sendToAishaAI(const std::vector<float>& audio)
{
    try {
        // Сохраняем аудио в WAV
        std::string wav_file = "/tmp/recognizer_audio.wav";
        saveAudioToWav(audio, wav_file);

        std::cout << "🔄 Отправляю аудио на Aisha AI...\n";

        // Подключаемся к Python сервису на 5001
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            std::cerr << "❌ Ошибка создания сокета\n";
            return "";
        }

        sockaddr_in server_addr{};
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(5001);
        inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);

        if (connect(sock, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            std::cerr << "❌ Не удалось подключиться к Python сервису на 5001\n";
            std::cerr << "   Убедись что запущен: python stt_service.py\n";
            close(sock);
            return "";
        }

        // Читаем WAV файл
        std::ifstream file(wav_file, std::ios::binary);
        if (!file) {
            close(sock);
            return "";
        }

        std::string wav_data((std::istreambuf_iterator<char>(file)), 
                             std::istreambuf_iterator<char>());
        file.close();

        // Multipart form data для отправки файла
        std::string boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
        std::string body = 
            "--" + boundary + "\r\n"
            "Content-Disposition: form-data; name=\"audio\"; filename=\"audio.wav\"\r\n"
            "Content-Type: audio/wav\r\n\r\n" +
            wav_data + "\r\n"
            "--" + boundary + "--\r\n";

        std::string request = 
            "POST /transcribe HTTP/1.1\r\n"
            "Host: 127.0.0.1:5001\r\n"
            "Content-Type: multipart/form-data; boundary=" + boundary + "\r\n"
            "Content-Length: " + std::to_string(body.length()) + "\r\n"
            "Connection: close\r\n"
            "\r\n";

        send(sock, request.c_str(), request.length(), 0);
        send(sock, body.c_str(), body.length(), 0);
        
        // Читаем ответ
        char buffer[8192] = {0};
        std::string response;
        while (recv(sock, buffer, sizeof(buffer), 0) > 0) {
            response += buffer;
            memset(buffer, 0, sizeof(buffer));
        }
        close(sock);

        // Парсим JSON ответ
        // Находим JSON часть (после пустой строки в HTTP ответе)
        size_t json_start = response.find("\r\n\r\n");
        if (json_start != std::string::npos) {
            json_start += 4;
            std::string json_str = response.substr(json_start);
            
            // Удаляем мусор после JSON
            size_t json_end = json_str.find('}');
            if (json_end != std::string::npos) {
                json_str = json_str.substr(0, json_end + 1);
            }

            // Простой парсинг JSON (ищем "text": "...")
            size_t text_pos = json_str.find("\"text\"");
            if (text_pos != std::string::npos) {
                size_t start = json_str.find(':', text_pos) + 1;
                while (start < json_str.length() && json_str[start] != '"') start++;
                start++; // пропускаем кавычку
                
                size_t end = start;
                while (end < json_str.length() && json_str[end] != '"') end++;
                
                std::string text = json_str.substr(start, end - start);
                
                if (!text.empty()) {
                    std::cout << "\n🎤 Aisha AI распознала: " << text << "\n";
                    std::cout << "════════════════════════════════════════\n";
                    return text;
                }
            }
        }

        std::cout << "⚠️  Aisha AI не распознала речь\n";
        return "";

    } catch (const std::exception& e) {
        std::cerr << "❌ Ошибка: " << e.what() << "\n";
        return "";
    }
}

bool Recognizer::acceptWaveform(const std::vector<float>& audio)
{
    if (audio.size() < 800) return false;
    
    // Отправляем на Aisha AI и сохраняем результат
    last_result = sendToAishaAI(audio);
    
    return !last_result.empty();
}

std::string Recognizer::forceFinalResult() const
{
    return last_result;
}

std::string Recognizer::getResult() const
{
    return last_result;
}

std::string Recognizer::getPartialResult() const
{
    return "";
}