# AudioTranscripY - Real-Time Speech Transcription

A lightweight, efficient real-time speech transcription system with automatic speaker identification. This tool captures audio from your microphone, processes it on-the-fly, and produces formatted transcripts with timestamps and speaker labels.

## Features

- **Real-time transcription** using OpenAI's Whisper model (tiny version)
- **Automatic speaker identification** using machine learning (K-means clustering)
- **Multi-speaker support** with clear speaker labels (Speaker 1, Speaker 2, etc.)
- **Timestamped output** for precise conversation logging
- **Optimized for speed** with minimal latency and reasonable accuracy
- **Clean, professional output** formatting
- **Automatic transcript saving** to text files with timestamps
- **Emergency Call ML Interpretation** ✨ NEW! - Classifies emergency calls with address extraction and incident routing

## Requirements

- Python 3.8+
- A working microphone
- Approximately 1GB of RAM for model and processing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/katgharalad/audiotranscripy.git
   cd audiotranscripy
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
   - List available audio input devices (optional)
   - Load the Whisper speech recognition model
   - Begin capturing and transcribing audio from your microphone

3. Speak clearly into your microphone:
   - The tool will transcribe your speech in real-time
   - Different speakers will be labeled automatically (Speaker 1, Speaker 2, etc.)
   - Transcriptions will appear with timestamps

4. Press ENTER at any time to stop recording
   - The complete transcript will be saved automatically to a file in the current directory
   - The filename will include the date and time of the recording

### Using the ML Interpretation Layer for Emergency Calls

For emergency dispatch scenarios, you can use the ML interpretation layer to automatically classify incidents, extract addresses, and identify casualties from transcripts.

1. To run the integrated system:
```
python ml_interpretation/integration.py
```

2. For more information, see the integration guide:
```
cat INTEGRATION.md
```

3. To run various demo modes:
```
python ml_interpretation/integrated_demo.py --mode all
```

4. Available modes:
   * `all` - Run all components
   * `audio` - Simulate audio transcripts
   * `router` - Test incident routing
   * `interpreter` - Test transcript interpretation
   * `test` - Run performance tests
   * `enhanced` - Test enhanced features
   * `visualize` - Generate visualizations

## How It Works

### Audio Processing
- Captures audio through the `sounddevice` library
- Processes audio in small chunks (buffer size: 64000 samples)
- Detects speech vs. silence using volume thresholds
- Batches audio data for efficient processing

### Speech Recognition
- Uses OpenAI's Whisper model (tiny variant) via `faster-whisper`
- Optimized for low latency with reasonable accuracy
- Processes audio incrementally as you speak

### Speaker Identification
- Uses K-means clustering to identify different speakers
- Extracts acoustic features (MFCCs, spectral centroid, etc.)
- Maintains speaker consistency with a temporal smoothing system
- Adapts to different voices over time

### Output Processing
- Formats transcripts with clear speaker labels and timestamps
- Merges consecutive utterances from the same speaker
- Filters out repetitions and common speech artifacts
- Saves complete transcript to a text file when finished

### Emergency Call Interpretation
- Identifies incident types (fire type, gas leak, etc.)
- Extracts address information from transcripts
- Classifies casualty information
- Determines priority level (HIGH, URGENT, CRITICAL)
- Validates addresses against a database
- Routes incidents to appropriate handlers
- Provides confidence scores for ML predictions
- Flags low-confidence cases for verification

## Limitations

- Speaker identification works best with distinct voices
- Background noise can affect transcription quality
- Very quiet speech might not be detected
- Accuracy is traded for speed - some words may be misinterpreted

## Advanced ML Features

The ML interpretation layer includes several enhanced features:

- **Confidence Scores**: ML model prediction confidence is surfaced
- **Address Validation**: Addresses are validated against Delaware's database
- **Priority Prediction**: Incidents are assigned priority levels for dispatch
- **Structured Casualties**: Casualties are categorized (children, elderly, pets, caller)
- **Verification Queue**: Low-confidence predictions are flagged for verification

For more details, see the ML interpretation layer's [README.md](ml_interpretation/README.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Created by katgharalad 