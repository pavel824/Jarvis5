#include <iostream>
#include <thread>
#include <atomic>
#include <filesystem>
#include <chrono>
#include <string>
#include <vector>
#include <mutex>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

#include "src/audioCapture.h"
#include "src/recognizer.h"

// Простой HTTP POST запрос к Python серверу
bool sendToPythonServer(const std::string& text) {
    try {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) return false;

        sockaddr_in server_addr{};
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(5000);
        inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);

        if (connect(sock, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            close(sock);
            return false;
        }

        // JSON payload
        std::string json_payload = R"({"text": ")" + text + R"(", "language": "uz"})";
        
        // HTTP POST запрос
        std::string request = 
            "POST /process_speech HTTP/1.1\r\n"
            "Host: 127.0.0.1:5000\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: " + std::to_string(json_payload.length()) + "\r\n"
            "Connection: close\r\n"
            "\r\n" + json_payload;

        send(sock, request.c_str(), request.length(), 0);
        
        // Читаем ответ
        char buffer[4096] = {0};
        recv(sock, buffer, sizeof(buffer), 0);
        close(sock);
        
        std::cout << "📤 Отправлено Python серверу: " << text << "\n";
        return true;
    } catch (...) {
        return false;
    }
}

int main(int argc, char* argv[])
{
    try
    {
        std::filesystem::path exe_path = std::filesystem::canonical(argv[0]);
        std::filesystem::path project_root = exe_path.parent_path().parent_path();

        std::string model_path = (project_root / "src" / "models" / "vosk-model-small-uz-0.22").string();

        Recognizer recognizer(model_path);
        
        std::vector<int> clients;
        std::mutex clientMutex;

        AudioCapture audioCapture;
        audioCapture.start();

        std::atomic<bool> running{true};

        // Обработка аудио с AI мозгом
        std::thread audioThread([&]()
        {
            const size_t block_size = 3200;
            auto last_speech_time = std::chrono::steady_clock::now();
            const float silence_threshold = 0.008f;
            const int force_final_after_ms = 1100;

            while (running)
            {
                std::vector<float> buf = audioCapture.getAudioBuffer();
                if (buf.size() < block_size)
                {
                    std::this_thread::sleep_for(std::chrono::milliseconds(20));
                    continue;
                }

                size_t pos = 0;
                while (pos + block_size <= buf.size())
                {
                    std::vector<float> chunk(buf.begin() + pos, buf.begin() + pos + block_size);

                    float vol = audioCapture.getVolume();
                    if (vol > silence_threshold)
                        last_speech_time = std::chrono::steady_clock::now();

                    bool final = recognizer.acceptWaveform(chunk);

                    pos += block_size;
                }

                auto silence_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::steady_clock::now() - last_speech_time).count();

                if (silence_ms > force_final_after_ms)
                {
                    std::string text = recognizer.forceFinalResult();
                    if (!text.empty()) {
                        std::cout << "\n🎤 РАСПОЗНАНО: " << text << "\n";
                        std::cout << "════════════════════════════════════════\n";
                        
                        // Отправляем на Python для обработки
                        sendToPythonServer(text);
                        
                        // Очищаем распознаватель для следующего ввода
                        recognizer.reset();
                    }
                }

                audioCapture.clearAudioBuffer(pos);
                std::this_thread::sleep_for(std::chrono::milliseconds(15));
            }
        });

        std::cout << "════════════════════════════════════════\n";
        std::cout << "🎤 JARVIS 5 - Қўя Алгоритми Асистenti\n";
        std::cout << "🧠 Қудратига Qwen AI\n";
        std::cout << "════════════════════════════════════════\n";
        std::cout << "✅ Ўзбек тилида сўзлашуни кутмоқда...\n";
        std::cout << "🔊 Говорите в микрофон (Enter для выхода)\n";
        std::cout << "════════════════════════════════════════\n";
        
        std::cin.get();

        running = false;
        audioCapture.stop();

        {
            std::lock_guard<std::mutex> lock(clientMutex);
            for (int c : clients) close(c);
            clients.clear();
        }

        if (audioThread.joinable()) audioThread.join();
        
        std::cout << "✅ Программа завершена\n";
    }
    catch (const std::exception& e)
    {
        std::cerr << "❌ Ошибка: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}