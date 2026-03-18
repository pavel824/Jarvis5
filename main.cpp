#include <iostream>
#include <thread>
#include <atomic>
#include <filesystem>
#include <chrono>
#include <string>
#include <vector>
#include <mutex>
#include <unistd.h>

#include "src/audioCapture.h"
#include "src/recognizer.h"

int main(int argc, char* argv[])
{
    try
    {
        std::filesystem::path exe_path = std::filesystem::canonical(argv[0]);
        std::filesystem::path project_root = exe_path.parent_path().parent_path();

        // Для Aisha нужен API ключ вместо пути к модели
        std::string aisha_api_key = "не покажу нахуй";

        Recognizer recognizer(aisha_api_key);
        
        AudioCapture audioCapture;
        audioCapture.start();

        std::atomic<bool> running{true};

        // Обработка аудио
        std::thread audioThread([&]()
        {
            const size_t sample_rate = 16000;
            const size_t silence_duration_ms = 800;
            const size_t silence_samples = (sample_rate * silence_duration_ms) / 1000;
            const float silence_threshold = 0.01f;
            
            std::vector<float> audio_buffer;
            size_t silence_counter = 0;

            while (running)
            {
                std::vector<float> buf = audioCapture.getAudioBuffer();
                if (buf.empty()) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(50));
                    continue;
                }

                float vol = audioCapture.getVolume();

                if (vol > silence_threshold) {
                    audio_buffer.insert(audio_buffer.end(), buf.begin(), buf.end());
                    silence_counter = 0;
                    std::cout << "🎤 Слушаю... (громкость: " << vol << ")\r";
                    std::cout.flush();
                } else {
                    if (!audio_buffer.empty()) {
                        silence_counter += buf.size();
                        
                        if (silence_counter > silence_samples) {
                            if (audio_buffer.size() > sample_rate) {
                                std::cout << "\n✅ Записано " << (audio_buffer.size() / sample_rate) << " сек\n";
                                
                                recognizer.acceptWaveform(audio_buffer);
                            }
                            
                            audio_buffer.clear();
                            silence_counter = 0;
                        }
                    }
                }

                audioCapture.clearAudioBuffer(buf.size());
                std::this_thread::sleep_for(std::chrono::milliseconds(30));
            }
        });

        std::cout << "════════════════════════════════════════\n";
        std::cout << "🎤 JARVIS 5 - Aisha AI STT\n";
        std::cout << "════════════════════════════════════════\n";
        std::cout << "✅ Ўзбек тилида сўзлашуни кутмоқда...\n";
        std::cout << "🔊 Говорите в микрофон (Enter для выхода)\n";
        std::cout << "════════════════════════════════════════\n";
        
        std::cin.get();

        running = false;
        audioCapture.stop();

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