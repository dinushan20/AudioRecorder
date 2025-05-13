import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from datetime import datetime
import os

# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_DIR = "recordings"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def list_audio_devices():
    """List available audio devices and categorize them as playback or recording devices."""
    p = pyaudio.PyAudio()
    playback_devices = []
    recording_devices = []

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info.get('name')
        max_input_channels = device_info.get('maxInputChannels')
        max_output_channels = device_info.get('maxOutputChannels')

        if max_output_channels > 0:
            playback_devices.append(device_name)

        if max_input_channels > 0:
            recording_devices.append(device_name)

    p.terminate()
    return playback_devices, recording_devices

def play_audio(file_path):
    """Play an audio file using PyAudio."""
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
    print("Playback finished")

def record_audio(filename_prefix="recording", duration=5):
    """Record audio from the default microphone and save it as a .wav file for the given duration."""
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording audio...")
    frames = []

    # Calculate the number of chunks to record based on the duration
    num_chunks = int(RATE / CHUNK * duration)

    for _ in range(num_chunks):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_DIR}/{filename_prefix}_{timestamp}.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Recording saved as {filename}")

    return filename

def save_spectrogram(file_path, filename_prefix="spectrogram"):
    """Generate and save a spectrogram image for a given audio file."""
    y, sr = librosa.load(file_path, sr=RATE)
    
    plt.figure(figsize=(10, 4))
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    librosa.display.specshow(librosa.power_to_db(S, ref=np.max), sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    spectrogram_filename = f"{OUTPUT_DIR}/{filename_prefix}_{timestamp}.png"
    plt.savefig(spectrogram_filename)
    plt.close()
    print(f"Spectrogram saved as {spectrogram_filename}")

    return spectrogram_filename
