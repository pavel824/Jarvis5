#include "recognizer.h"
#include <stdexcept>
#include <vector>
#include <algorithm>
#include <cstring>

Recognizer::Recognizer(const std::string& model_path)
{
    model = vosk_model_new(model_path.c_str());
    if (!model) throw std::runtime_error("Не удалось загрузить модель: " + model_path);

    recognizer = vosk_recognizer_new(model, 16000.0f);
    if (!recognizer) {
        vosk_model_free(model);
        throw std::runtime_error("Не удалось создать VoskRecognizer");
    }
}

Recognizer::~Recognizer()
{
    if (recognizer) vosk_recognizer_free(recognizer);
    if (model)      vosk_model_free(model);
}

void Recognizer::reset() { if (recognizer) vosk_recognizer_reset(recognizer); }

bool Recognizer::acceptWaveform(const std::vector<float>& audio)
{
    if (audio.size() < 800) return false;

    std::vector<short> pcm(audio.size());
    for (size_t i = 0; i < audio.size(); ++i) {
        float s = std::clamp(audio[i], -1.0f, 1.0f);
        pcm[i] = static_cast<short>(s * 32767.0f);
    }

    return vosk_recognizer_accept_waveform(recognizer,
        reinterpret_cast<const char*>(pcm.data()), static_cast<int>(pcm.size())) != 0;
}

// Принудительный финал — решает проблему "не слышит последние слова"
std::string Recognizer::forceFinalResult() const
{
    if (!recognizer) return "";

    const char* json = vosk_recognizer_final_result(recognizer);
    if (!json) return "";

    std::string s(json);
    size_t pos = s.find("\"text\" : \"");
    if (pos == std::string::npos) return "";

    pos += 10;
    size_t end = s.find('"', pos);
    if (end == std::string::npos) return "";

    std::string text = s.substr(pos, end - pos);

    // очистка мусора для узбекской модели
    text.erase(std::remove_if(text.begin(), text.end(), [](unsigned char c){
        return (c < 32 && c != ' ' && c != '\'' && c != '-') || c > 127;
    }), text.end());

    text.erase(0, text.find_first_not_of(" \t\n\r"));
    text.erase(text.find_last_not_of(" \t\n\r") + 1);

    return text;
}

std::string Recognizer::getResult() const
{
    if (!recognizer) return "";
    const char* json = vosk_recognizer_result(recognizer);
    if (!json) return "";

    std::string s(json);
    size_t pos = s.find("\"text\" : \"");
    if (pos == std::string::npos) return "";
    pos += 10;
    size_t end = s.find('"', pos);
    if (end == std::string::npos) return "";
    return s.substr(pos, end - pos);
}

std::string Recognizer::getPartialResult() const
{
    if (!recognizer) return "";
    const char* json = vosk_recognizer_partial_result(recognizer);
    if (!json) return "";

    std::string s(json);
    size_t pos = s.find("\"partial\" : \"");
    if (pos == std::string::npos) return "";
    pos += 13;
    size_t end = s.find('"', pos);
    if (end == std::string::npos) return "";
    return s.substr(pos, end - pos);
}
