from PyQt5 import QtWidgets
from audio_utils import play_audio, record_audio, save_spectrogram, list_audio_devices
import threading
import wave

class AudioApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(AudioApp, self).__init__()
        self.audio_file_path = None  # Store the imported audio file path
        self.init_ui()
        self.playback_thread = None
        self.record_thread = None
        self.populate_audio_devices()

    def init_ui(self):
        self.setWindowTitle("Audio Recording & Playback Application")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Top section: Import sound and device selection
        top_layout = QtWidgets.QHBoxLayout()
        self.import_button = QtWidgets.QPushButton("Import Sound", self)
        top_layout.addWidget(self.import_button)

        self.playback_dropdown = QtWidgets.QComboBox(self)
        self.playback_dropdown.addItem("Select Playback Device")
        top_layout.addWidget(self.playback_dropdown)

        self.recording_dropdown = QtWidgets.QComboBox(self)
        self.recording_dropdown.addItem("Select Recording Device")
        top_layout.addWidget(self.recording_dropdown)

        main_layout.addLayout(top_layout)

        # Middle section: Start and Stop Recording buttons
        control_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Start Recording", self)
        self.stop_button = QtWidgets.QPushButton("Stop Recording", self)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)

        main_layout.addLayout(control_layout)

        # Connect buttons to functions
        self.import_button.clicked.connect(self.import_sound)
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

    def populate_audio_devices(self):
        """Populate the playback and recording device dropdowns."""
        playback_devices, recording_devices = list_audio_devices()

        # Populate playback dropdown
        for device in playback_devices:
            self.playback_dropdown.addItem(device)

        # Populate recording dropdown
        for device in recording_devices:
            self.recording_dropdown.addItem(device)

    def import_sound(self):
        # Logic to import audio files
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3)")
        if file_path:
            self.audio_file_path = file_path
            print(f"Imported audio file: {file_path}")

    def calculate_total_duration(self):
        """Calculate the total duration of the audio clip in seconds."""
        if self.audio_file_path:
            with wave.open(self.audio_file_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                print(f"Duration of {self.audio_file_path}: {duration} seconds")
                return duration
        return 0

    def start_recording(self):
        if self.playback_dropdown.currentText() != "Select Playback Device" and \
           self.recording_dropdown.currentText() != "Select Recording Device" and \
           self.audio_file_path is not None:
            
            # Calculate the total duration of the audio file
            total_duration = self.calculate_total_duration()
            
            # Start playback and recording threads with total duration
            self.playback_thread = threading.Thread(target=play_audio, args=(self.audio_file_path,))
            self.record_thread = threading.Thread(target=self.record_and_generate_spectrogram, args=(total_duration,))
            self.playback_thread.start()
            self.record_thread.start()
            print("Recording started")
        else:
            print("Please select both playback and recording devices and import an audio file.")

    def record_and_generate_spectrogram(self, total_duration):
        # Record audio and save the file with the calculated total duration
        recording_path = record_audio("MyRecording", total_duration)

        # Generate the spectrogram outside the thread
        self.generate_spectrogram(recording_path)

    def generate_spectrogram(self, recording_path):
        # Generate spectrogram in the main thread after recording
        save_spectrogram(recording_path, "MySpectrogram")
        print("Recording and spectrogram generation complete")

    def stop_recording(self):
        # Logic to stop playback and recording
        if self.playback_thread and self.record_thread:
            print("Stopping recording")
            # Implement stopping logic here if necessary
        else:
            print("Recording is not in progress")
