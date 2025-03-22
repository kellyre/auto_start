import sys
import time
import threading
import numpy as np
import sounddevice as sd
import whisper
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QTextEdit, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import pyttsx3
from skills_manager import SkillsManager
from command_processor import CommandProcessor
from whisper_integration import create_whisper_recognizer, WhisperTranscriber
from auto_settings import Settings

class SignalEmitter(QObject):
    status_changed = pyqtSignal(str)

class VoiceCommandApp:
    def __init__(self):
        # Initialize settings
        self.settings = Settings()
        
        # Other initializations...
        self.skills_manager = SkillsManager()
        self.command_processor = CommandProcessor(self.skills_manager)
        self.signal_emitter = SignalEmitter()
        self.audio_buffer = []
        self.is_recording = False
        self.listening = True
        self.current_skill = None
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Get saved device from settings
        self.selected_device = self.settings.get("audio", "device_id")
        
        # Initialize Whisper recognizer
        self.recognizer = WhisperTranscriber()
        
        # Initialize UI
        self.app = QApplication(sys.argv)
        self.init_ui()
        
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()

    def init_ui(self):
        # Create main window
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("Voice Assistant")
        self.main_window.setGeometry(100, 100, 400, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        menu_bar = self.main_window.menuBar()
        settings_menu = menu_bar.addMenu("Settings")
        
        # Add Whisper model selection to settings menu
        whisper_menu = settings_menu.addMenu("Whisper Model")
        
        model_options = {
            "tiny": "Tiny (Fastest)",
            "base": "Base (Fast)",
            "small": "Small (Balanced)",
            "medium": "Medium (Accurate)",
            "large": "Large (Most Accurate)"
        }
        
        # Get current model from settings
        current_model = self.settings.get("whisper", "model", "tiny")
        
        for model_name, display_name in model_options.items():
            action = whisper_menu.addAction(display_name)
            action.setCheckable(True)
            action.setChecked(model_name == current_model)
            action.triggered.connect(lambda checked, m=model_name: self.set_whisper_model(m))
        
        # Add microphone selection
        mic_label = QLabel("Select Microphone:")
        layout.addWidget(mic_label)
        
        self.mic_combo = QComboBox()
        self.populate_microphones()  # Add this line to populate the dropdown
        self.mic_combo.currentIndexChanged.connect(self.select_microphone)
        layout.addWidget(self.mic_combo)
        
        # Add listen button
        self.listen_button = QPushButton("Listen")
        self.listen_button.clicked.connect(self.start_listening)
        layout.addWidget(self.listen_button)
        
        # Add status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Add commands list
        commands_label = QLabel("Available Commands:")
        layout.addWidget(commands_label)
        
        self.commands_list = QTextEdit()
        self.commands_list.setReadOnly(True)
        layout.addWidget(self.commands_list)
        
        # Connect signals
        self.signal_emitter.status_changed.connect(self.status_label.setText)
        
        # Show the window
        self.main_window.show()
        
        # Update commands list
        self.update_commands_list()

    def listen_loop(self):
        while True:
            if not self.listening:
                time.sleep(0.5)
                continue
                
            try:
                # Clear previous audio buffer
                self.audio_buffer = []
                self.is_recording = True
                
                # Start recording with selected device
                device_info = None
                if self.selected_device is not None:
                    device_info = sd.query_devices(self.selected_device)
                
                # Get sample rate from settings or use default
                sample_rate = self.settings.get("audio", "sample_rate", 16000)
                
                with sd.InputStream(device=self.selected_device, 
                                   callback=self.audio_callback,
                                   channels=1,
                                   samplerate=sample_rate):
                    self.signal_emitter.status_changed.emit("Listening")
                    # Wait for audio
                    time.sleep(5)
                    self.is_recording = False
                
                # Process the audio with Whisper
                try:
                    text = self.process_audio()
                    print(f"Recognized: {text}")
                    
                    if not text:
                        continue
                    
                    if self.current_skill and "cancel" in text.lower():
                        self.current_skill = None
                        self.signal_emitter.status_changed.emit("Cancelled - Listening")
                        continue
                    
                    # Process the command
                    self.process_command(text)
                    
                except Exception as e:
                    print(f"Error processing audio: {e}")
                    self.signal_emitter.status_changed.emit("Error processing audio")
                
            except Exception as e:
                print(f"Error recording audio: {e}")
                self.signal_emitter.status_changed.emit("Error recording audio")
                self.is_recording = False

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        
        if self.is_recording:
            # Store audio data for processing
            self.audio_buffer.append(indata.copy())
        
    def process_audio(self):
        if not self.audio_buffer:
            return ""
            
        # Concatenate all audio chunks
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        
        # Process with Whisper
        try:
            # Convert to float32 if needed
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Flatten if stereo
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()
            
            # Normalize if needed
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
                
            # Use Whisper to transcribe
            result = self.recognizer.model.transcribe(audio_data, fp16=False)
            return result["text"]
        except Exception as e:
            print(f"Error in process_audio: {e}")
            return ""
        
    def setup_ui(self):
        # Create application window
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("Voice Command Assistant")
        self.window.setGeometry(100, 100, 500, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Add status label
        self.status_label = QLabel("Starting...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Add microphone selection
        mic_layout = QHBoxLayout()
        mic_label = QLabel("Microphone:")
        self.mic_combo = QComboBox()
        self.populate_microphones()
        self.mic_combo.currentIndexChanged.connect(self.select_microphone)
        
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combo)
        layout.addLayout(mic_layout)
        
        # Add refresh button for microphones
        refresh_button = QPushButton("Refresh Microphones")
        refresh_button.clicked.connect(self.populate_microphones)
        layout.addWidget(refresh_button)
        
        # Add toggle button
        self.toggle_button = QPushButton("Pause Listening")
        self.toggle_button.clicked.connect(self.toggle_listening)
        layout.addWidget(self.toggle_button)
        
        # Add available commands label
        commands_label = QLabel("Available Commands:")
        layout.addWidget(commands_label)
        
        self.commands_list = QLabel()
        self.update_commands_list()
        layout.addWidget(self.commands_list)
        
        # Set layout and central widget
        central_widget.setLayout(layout)
        self.window.setCentralWidget(central_widget)
        
        # Connect signal to update status
        self.signal_emitter.status_changed.connect(self.update_status)
    
    def populate_microphones(self):
        self.mic_combo.clear()
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                self.mic_combo.addItem(f"{i}: {device['name']}", i)
    
    def select_microphone(self, index):
        if index >= 0:
            device_id = self.mic_combo.itemData(index)
            device_name = self.mic_combo.itemText(index)
            
            self.selected_device = device_id
            print(f"Selected microphone: {device_name}")
            
            # Save the selected device to settings
            self.settings.set_audio_device(device_id, device_name)
    
    def update_commands_list(self):
        commands_text = ""
        for name, skill in self.skills_manager.get_all_skills().items():
            commands_text += f"• {name}: {skill.description}\n"
        
        self.commands_list.setText(commands_text)
        
    def toggle_listening(self):
        """Toggle listening state"""
        self.listening = not self.listening
        if self.listening:
            self.listen_button.setText("Stop Listening")
            self.signal_emitter.status_changed.emit("Listening")
            self.speak("Listening enabled")
        else:
            self.listen_button.setText("Start Listening")
            self.signal_emitter.status_changed.emit("Not Listening")
            self.speak("Listening disabled")
    
    def update_status(self, status):
        self.status_label.setText(status)
    
    def run(self):
        """Run the application"""
        sys.exit(self.app.exec_())

    def start_listening(self):
        """Start listening for commands"""
        self.listening = True
        self.listen_button.setText("Stop Listening")
        self.signal_emitter.status_changed.emit("Listening")
        self.speak("Listening for commands")

    def set_whisper_model(self, model_name):
        """Change the Whisper model"""
        # Update the settings
        self.settings.set("whisper", "model", model_name)
        
        # Update the menu checkmarks
        for action in self.main_window.menuBar().findChild(QMenu, "Whisper Model").actions():
            action.setChecked(action.text().startswith(model_name.capitalize()))
        
        # Show status message
        self.signal_emitter.status_changed.emit(f"Whisper model changed to {model_name}")
        
        # Reload the model in the transcriber
        if hasattr(self, 'transcriber'):
            self.transcriber.set_model(model_name)

    def process_command(self, text):
        """Process the recognized text as a command"""
        self.signal_emitter.status_changed.emit(f"Processing: {text}")
        
        # If we're in the middle of a skill that needs confirmation
        if self.current_skill:
            if "yes" in text.lower() or "confirm" in text.lower():
                self.signal_emitter.status_changed.emit(f"Executing: {self.current_skill[0]}")
                self.speak(f"Executing {self.current_skill[0]}")
                success = self.current_skill[1]()
                self.current_skill = None
                self.signal_emitter.status_changed.emit("Listening")
                return
            elif "no" in text.lower() or "cancel" in text.lower():
                self.speak("Cancelled")
                self.current_skill = None
                self.signal_emitter.status_changed.emit("Listening")
                return
        
        # Process the command to find matching skill
        skill_name, skill_action = self.command_processor.process_command(text)
        
        if skill_name and skill_action:
            self.current_skill = (skill_name, skill_action)
            confirmation = f"Do you want to execute {skill_name}?"
            self.signal_emitter.status_changed.emit(confirmation)
            self.speak(confirmation)
        else:
            # No matching skill found, try to answer as a question
            self.signal_emitter.status_changed.emit("No matching skill found")
            self.speak("I don't know how to do that yet")

    def speak(self, text):
        """Use text-to-speech to respond to the user"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

if __name__ == "__main__":
    app = VoiceCommandApp()
    app.run()



