# AudioTranscripY - Real-Time Speech Transcription

A lightweight, efficient real-time speech transcription system with automatic speaker identification. This tool captures audio from your microphone, processes it on-the-fly, and produces formatted transcripts with timestamps and speaker labels.

## Features

* **Real-time transcription** using OpenAI's Whisper model (tiny version)
* **Automatic speaker identification** using machine learning (K-means clustering)
* **Multi-speaker support** with clear speaker labels (Speaker 1, Speaker 2, etc.)
* **Timestamped output** for precise conversation logging
* **Optimized for speed** with minimal latency and reasonable accuracy
* **Clean, professional output** formatting
* **Automatic transcript saving** to text files with timestamps
* **Emergency Call ML Interpretation** - Classifies emergency calls with address extraction and incident routing

## Requirements

* Python 3.8+
* A working microphone
* Approximately 1GB of RAM for model and processing

## Installation

1. Clone this repository:  
```  
git clone https://github.com/katgharalad/audiotrancriptionfire.git  
cd audiotrancriptionfire  
```
2. Create a virtual environment (recommended):  
```  
python -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate  
```
3. Install the required packages:  
```  
pip install -r requirements.txt  
```
4. If you want to use the ML interpretation layer, install its dependencies:

```
pip install -r ml_interpretation/requirements.txt
```

## Usage

1. Run the main script:  
```  
python main.py  
```
2. The system will:  
   * List available audio input devices (optional)  
   * Load the Whisper speech recognition model  
   * Begin capturing and transcribing audio from your microphone
3. Speak clearly into your microphone:  
   * The tool will transcribe your speech in real-time  
   * Different speakers will be labeled automatically (Speaker 1, Speaker 2, etc.)  
   * Transcriptions will appear with timestamps
4. Press ENTER at any time to stop recording  
   * The complete transcript will be saved automatically to a file in the current directory  
   * The filename will include the date and time of the recording

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created by katgharalad