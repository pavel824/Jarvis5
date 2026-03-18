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
#include <unistd.h>

#include "src/audioCapture.h"
#include "src/recognizer.h"

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

        // TCP сервер
        std::thread serverThread([&running, &clients, &clientMutex]()
        {
            int server_fd = socket(AF_INET, SOCK_STREAM, 0);
            if (server_fd < 0) return;

            int opt = 1;
            setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

            sockaddr_in address{};
            address.sin_family = AF_INET;
            address.sin_addr.s_addr = INADDR_ANY;
            address.sin_port = htons(8080);

            if (bind(server_fd, (sockaddr*)&address, sizeof(address)) < 0) {
                close(server_fd);
                return;
            }

            listen(server_fd, 10);
            std::cout << "✅ API сервер на порту 8080\n";

            while (running)
            {
                int client = accept(server_fd, nullptr, nullptr);
                if (client >= 0)
                {
                    std::lock_guard<std::mutex> lock(clientMutex);
                    clients.push_back(client);
                    std::cout << "👤 Клиент подключился\n";
                }
            }
            close(server_fd);
        });

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
        std::cout << "Enter ни босинг чиқиш учун\n";
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
        if (serverThread.joinable()) serverThread.join();
        
        std::cout << "✅ Жарвис янаён...\n";
    }
    catch (const std::exception& e)
    {
        std::cerr << "❌ Ошибка: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}