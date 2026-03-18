#pragma once

#include <string>
#include <vector>

class Recognizer {
public:
    explicit Recognizer(const std::string& api_key);
    ~Recognizer();

    bool acceptWaveform(const std::vector<float>& audio);
    std::string getResult() const;
    std::string forceFinalResult() const;
    std::string getPartialResult() const;
    void reset();

private:
    std::string sendToAishaAI(const std::vector<float>& audio);
    void saveAudioToWav(const std::vector<float>& audio, const std::string& filename);

    std::string api_key;
    mutable std::string last_result;
};