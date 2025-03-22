# Voice Command Assistant

A Python-based voice command assistant that uses OpenAI's Whisper for speech recognition and provides an extensible framework for voice-activated skills.

## Features

- Offline speech recognition using OpenAI's Whisper model
- Modular skill system for easy extension
- Simple PyQt5-based user interface
- Support for command cancellation
- Extensible architecture for adding new voice commands

## Installation

### Prerequisites

- Python 3.8 or higher
- PyAudio (which may require additional steps to install)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/kellyre/auto_start.git
   cd auto_start
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

The application will start listening for voice commands. Speak clearly into your microphone to issue commands.

### Available Commands

- "Open [application name]" - Opens the specified application
- "Cancel" - Cancels the current command (when a skill is active)

## Adding New Skills

Create a new Python file in the `skills` directory:

```python
# skills/my_new_skill.py
def my_new_skill():
    """
    This skill does something awesome
    """
    print("Executing my new skill!")
    # Your skill implementation here

# Register the skill with a command phrase
COMMANDS = {
    "do something awesome": my_new_skill
}
```

The skill will be automatically discovered and registered when the application starts.

## Whisper Model Options

The application uses Whisper's "tiny" model by default. You can change this in `whisper_integration.py` to one of:

- "tiny" - Fastest, least accurate
- "base" - Good balance for most use cases
- "small" - Better accuracy, requires more resources
- "medium" - High accuracy, slower
- "large" - Highest accuracy, requires significant resources

## License

MIT License - See LICENSE file for details.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the user interface
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) for the audio processing framework
