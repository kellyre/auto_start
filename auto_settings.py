import os
import json
from typing import Any, Dict, Optional

class Settings:
    """
    Handles application settings with automatic saving and loading.
    Settings are stored in a JSON file and accessed through get/set methods.
    """
    
    def __init__(self, settings_file: str = "user_settings.json"):
        """Initialize settings manager with default settings file"""
        self.settings_file = settings_file
        self.settings = {
            "audio": {
                "device_id": None,
                "device_name": "",
                "sample_rate": 16000
            },
            "whisper": {
                "model": "tiny",  # tiny, base, small, medium, large
                "language": "en"
            },
            "ui": {
                "theme": "system",
                "window_position": [100, 100],
                "window_size": [400, 500]
            },
            "tts": {
                "rate": 150,
                "volume": 1.0,
                "voice": None  # Use system default
            }
        }
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Load settings from file if it exists"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values, preserving defaults for missing keys
                    self._update_nested_dict(self.settings, loaded_settings)
                print(f"Settings loaded from {self.settings_file}")
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def _save_settings(self) -> None:
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """Update nested dictionary with another dictionary"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a setting value by section and key"""
        if section in self.settings and key in self.settings[section]:
            return self.settings[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set a setting value by section and key"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self._save_settings()
    
    def get_section(self, section: str) -> Dict:
        """Get an entire section of settings"""
        return self.settings.get(section, {})
    
    def set_audio_device(self, device_id: int, device_name: str) -> None:
        """Set the audio device settings"""
        self.settings["audio"]["device_id"] = device_id
        self.settings["audio"]["device_name"] = device_name
        self._save_settings()
    
    def set_whisper_model(self, model: str) -> None:
        """Set the Whisper model"""
        if model in ["tiny", "base", "small", "medium", "large"]:
            self.settings["whisper"]["model"] = model
            self._save_settings()
    
    def set_tts_settings(self, rate: Optional[int] = None, 
                         volume: Optional[float] = None, 
                         voice: Optional[str] = None) -> None:
        """Set text-to-speech settings"""
        if rate is not None:
            self.settings["tts"]["rate"] = rate
        if volume is not None:
            self.settings["tts"]["volume"] = volume
        if voice is not None:
            self.settings["tts"]["voice"] = voice
        self._save_settings()
    
    def save_window_position(self, x: int, y: int) -> None:
        """Save the window position"""
        self.settings["ui"]["window_position"] = [x, y]
        self._save_settings()
    
    def save_window_size(self, width: int, height: int) -> None:
        """Save the window size"""
        self.settings["ui"]["window_size"] = [width, height]
        self._save_settings()