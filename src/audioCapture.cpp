#define MINIAUDIO_IMPLEMENTATION
#include "audioCapture.h"
#include <cmath>
#include <stdexcept>
#include <algorithm>

AudioCapture::AudioCapture() 
    : volume(0.0f), noiseFloor(0.001f) 
{
    ma_device_config config = ma_device_config_init(ma_device_type_capture);
    config.capture.format = ma_format_f32;
    config.capture.channels = 1;
    config.sampleRate = 16000;
    config.dataCallback = dataCallback;
    config.pUserData = this;

    if (ma_device_init(NULL, &config, &device) != MA_SUCCESS) {
        throw std::runtime_error("Failed to initialize miniaudio device");
    }
}

AudioCapture::~AudioCapture() {
    ma_device_uninit(&device);
}

void AudioCapture::start() {
    ma_device_start(&device);
}

void AudioCapture::stop() {
    ma_device_stop(&device);
}

void AudioCapture::clearAudioBuffer(size_t n) {
    std::lock_guard<std::mutex> lock(mutex);
    if (n >= audioBuffer.size()) {
        audioBuffer.clear();
    } else {
        audioBuffer.erase(audioBuffer.begin(), audioBuffer.begin() + n);
    }
}

std::vector<float> AudioCapture::getAudioBuffer() {
    std::lock_guard<std::mutex> lock(mutex);
    return audioBuffer;
}

float AudioCapture::getVolume() const {
    std::lock_guard<std::mutex> lock(mutex);
    return volume;
}

bool AudioCapture::isSpeechDetected() const {
    std::lock_guard<std::mutex> lock(mutex);
    return volume > (noiseFloor * 2.5f);
}

void AudioCapture::updateNoiseProfile(const std::vector<float>& chunk) {
    float sum = 0.0f;
    for (auto s : chunk) {
        sum += s * s;
    }
    float rms = std::sqrt(sum / chunk.size());
    
    noiseEstimate.push_back(rms);
    if (noiseEstimate.size() > 100) {
        noiseEstimate.pop_front();
    }
    
    if (noiseEstimate.size() > 10) {
        float min_val = *std::min_element(noiseEstimate.begin(), noiseEstimate.end());
        noiseFloor = min_val * 1.5f;
    }
}

void AudioCapture::dataCallback(ma_device* device, void* output, const void* input, ma_uint32 frameCount) {
    auto* self = static_cast<AudioCapture*>(device->pUserData);

    std::lock_guard<std::mutex> lock(self->mutex);
    const float* in = static_cast<const float*>(input);
    self->audioBuffer.insert(self->audioBuffer.end(), in, in + frameCount);

    float sum = 0.0f;
    for (ma_uint32 i = 0; i < frameCount; i++) {
        sum += in[i] * in[i];
    }
    self->volume = std::sqrt(sum / frameCount);
}