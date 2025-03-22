import whisper
import numpy as np
from auto_settings import Settings

class WhisperTranscriber:
    def __init__(self):
        self.settings = Settings()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model based on settings"""
        model_name = self.settings.get("whisper", "model", "tiny")
        try:
            self.model = whisper.load_model(model_name)
            print(f"Loaded Whisper model: {model_name}")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            # Fall back to tiny model if there's an error
            self.model = whisper.load_model("tiny")
    
    def transcribe(self, audio_data, sample_rate=16000):
        """Transcribe audio data using Whisper"""
        if self.model is None:
            self._load_model()
            
        if self.model is None:
            return ""
            
        # Convert audio data to the format expected by Whisper
        audio_data = np.array(audio_data).flatten().astype(np.float32) / 32768.0
        
        # Transcribe the audio
        result = self.model.transcribe(audio_data)
        
        return result["text"].strip()
    
    def set_model(self, model_name):
        """Change the Whisper model and save to settings"""
        if model_name in ["tiny", "base", "small", "medium", "large"]:
            self.settings.set("whisper", "model", model_name)
            self._load_model()
            return True
        return False

def create_whisper_recognizer():
    """Create and return a new WhisperTranscriber instance"""
    return WhisperTranscriber()

