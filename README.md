# 🗣️ OrthoLyse

<div align="center">
  <p><strong>Automated Transcription and Linguistic Analysis for Speech Therapy</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![PySide6](https://img.shields.io/badge/PySide6-Qt-green?style=for-the-badge&logo=qt)](https://doc.qt.io/qtforpython/)
  [![Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange?style=for-the-badge&logo=openai)](https://github.com/openai/whisper)
  [![Spacy](https://img.shields.io/badge/Spacy-NLP-09D3AC?style=for-the-badge&logo=spacy)](https://spacy.io/)

  ![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
  ![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square)
</div>

## 📋 Overview

**OrthoLyse** is a powerful desktop application designed specifically for **speech therapists (orthophonistes)**. It automates the transcription of audio recordings and performs advanced linguistic analysis to evaluate the syntactic complexity of patient speech.

By leveraging state-of-the-art AI models like **OpenAI Whisper** and **Spacy**, OrthoLyse saves professionals valuable time, allowing them to focus more on patient care and less on manual transcription and counting.

- 🎙️ **Automated Transcription**: Converts speech to text with high accuracy.
- 📊 **Linguistic Analysis**: Calculates key metrics instantly (MLU, words, morphemes).
- 📝 **Correction Interface**: Listen and edit transcriptions in real-time.
- 📄 **Report Generation**: Export detailed analysis reports in PDF.

## ✨ Features

### Core Functionalities
- **Smart Transcription**: Uses `OpenAI Whisper` to transcribe audio files or live recordings with impressive accuracy.
- **Real-Time Recording**: Record patient sessions directly within the app.
- **Interactive Correction**: Integrated audio player synchronized with text editor for easy verification and correction.
- **Linguistic Metrics**: innovative automatic calculation of:
  - Total number of words
  - Number of utterances
  - Mean Length of Utterance (MLU / AM)
  - Morphological complexity (using `Spacy` and `NLTK`)
- **Export Options**: Generate comprehensive PDF reports including the transcription and analysis results.

### User Interface
- **Modern UI**: Built with `PySide6` (Qt) for a responsive and professional look.
- **Easy Navigation**: Intuitive sidebar for switching between Recording, Importing, and Analysis views.
- **Waveform Visualization**: Visual feedback during recording and playback.

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Reasonably recent version recommended)
- **FFmpeg** (Required for audio processing by Whisper/Pydub)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/assinscreedFC/OrthoLyse.git
   cd OrthoLyse
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This might take a few minutes as it downloads large models (Whisper, Spacy).*

3. **Download Spacy Models**
   Ensure the French language models are installed:
   ```bash
   python -m spacy download fr_core_news_lg
   python -m spacy download fr_core_news_sm
   ```

## 📖 Usage

### Launch the Application
Execute the main script from the project root:
```bash
python app/main.py
```

### Workflow
1.  **Import or Record**:
    *   Click **"Importer un fichier"** to load an existing `.mp3` or `.wav` file.
    *   Or use the **"Enregistrement"** tab to record a session live.
2.  **Transcribe**:
    *   The app will automatically process the audio using Whisper.
3.  **Review & Correct**:
    *   Use the editor to read the transcription.
    *   Play the audio segment by segment to verify accuracy.
    *   Make any necessary manual corrections.
4.  **Analyze**:
    *   Click the **"Analyser"** button to compute linguistic metrics.
    *   View the results (Word count, MLU, etc.) in the dashboard.
5.  **Export**:
    *   Save the analysis as a PDF report for the patient's file.

## 🛠 Tech Stack

- **Language**: Python 3.12
- **GUI Framework**: PySide6 (Qt for Python)
- **Speech-to-Text**: OpenAI Whisper
- **NLP & Linguistics**: Spacy, NLTK
- **Audio Processing**: Pydub, PyAudio
- **PDF Generation**: FPDF2

## 📁 Project Structure

```
OrthoLyse/
├── app/
│   ├── main.py                 # Application entry point
│   ├── mainWindow.py           # Main GUI window setup
│   ├── Views/                  # UI Pages (Home, Import, Recording, Analysis)
│   ├── models/                 # Logic & Data handling
│   ├── controllers/            # Bridges between UI and Models
│   ├── assets/                 # Icons, images, styles
│   └── ...
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```

## 🤝 Contributing

Contributions are welcome! If you're a developer or a speech therapist with ideas:

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

## 📝 License

This project is intended for educational and professional assistance purposes.
Copyright © 2024 - 2026. All rights reserved.

---
<div align="center">
  <p>Built with ❤️ to support Speech Therapy Professionals</p>
</div>
