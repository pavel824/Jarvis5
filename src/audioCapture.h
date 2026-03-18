#pragma once

#include <library/miniaudio.h>
#include <vector>
#include <mutex>
#include <deque>

class AudioCapture {
public:
    AudioCapture();
    ~AudioCapture();

    void start();
    void stop();
    
    void clearAudioBuffer(size_t n);
    std::vector<float> getAudioBuffer();
    float getVolume() const;
    bool isSpeechDetected() const;

private:
    static void dataCallback(ma_device* device, void* output, const void* input, ma_uint32 frameCount);
    
    void updateNoiseProfile(const std::vector<float>& chunk);

    ma_device device;
    std::vector<float> audioBuffer;
    mutable std::mutex mutex;
    float volume;
    float noiseFloor;
    std::deque<float> noiseEstimate;
};