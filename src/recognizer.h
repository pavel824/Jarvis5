#pragma once

#include <string>
#include <vector>
#include <library/vosk_api.h>

class Recognizer {
public:
    explicit Recognizer(const std::string& model_path);
    ~Recognizer();

    bool acceptWaveform(const std::vector<float>& audio);
    std::string getResult() const;           // обычный результат
    std::string forceFinalResult() const;    // ← НОВОЕ: принудительный финал
    std::string getPartialResult() const;
    void reset();

private:
    VoskModel*      model     = nullptr;
    VoskRecognizer* recognizer = nullptr;
};
