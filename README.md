#  PulseLab Tuner

<img width="479" height="874" alt="Screenshot 2026-02-20 154552" src="https://github.com/user-attachments/assets/acfcb854-f0a9-432e-84ef-3faced462631" />
<img width="482" height="866" alt="Screenshot 2026-02-20 154542" src="https://github.com/user-attachments/assets/8859b998-2f69-4348-8ba7-4ba82c886bb4" />

A professional real-time **Tuner & Metronome** application built with Python and PySide6.

PulseLab Tuner provides accurate pitch detection using the YIN algorithm, a visually responsive needle meter, a progressive tempo training mode, and a clean modern GUI — all packaged as a standalone Windows executable.

---

##  Features

###  Tuner
- Real-time pitch detection using **YIN algorithm**
- Note name detection
- Frequency display (Hz)
- Cents deviation calculation
- Graphical needle meter
- Reference tone generator (Fork)
- Adjustable A4 calibration
- Volume control

###  Metronome
- Adjustable BPM
- Tap Tempo
- Time Signature support
- Accent beats
- Progressive Practice Mode (gradual tempo increase)
- Visual beat indicator
- Live tempo update display

###  System
- Modular architecture
- Settings auto-save (JSON)
- Graceful shutdown
- Standalone Windows executable
- Custom application icon

---
##  Project Structure

```
PulseLab_Tuner/
│
├── main.py
├── version.py
│
├── core/
│   ├── audio_engine.py
│   ├── tuner_engine.py
│   ├── metronome_engine.py
│   └── tone_generator.py
│
├── ui/
│   ├── main_window.py
│   ├── tuner_widget.py
│   ├── metronome_widget.py
│   ├── tuner_meter.py
│   └── styles.qss
│
├── utils/
│   └── settings_manager.py
│
├── assets/
│   ├── icon.png
│   └── PulseLab_Tuner.ico
│
└── dist/
    └── PulseLab_Tuner.exe
```

---

##  Installation

###  Option 1 – Run Executable (Windows)

Download the latest release and run:
PulseLab_Tuner.exe

text


No Python installation required.

---

###  Option 2 – Run from Source

1. Clone the repository:

```bash
git clone https://github.com/yourusername/PulseLab_Tuner.git
cd PulseLab_Tuner
Create virtual environment:
Bash

python -m venv venv
venv\Scripts\activate
Install dependencies:
Bash

pip install -r requirements.txt
Run:
Bash

python main.py
 Build Executable (Windows)
Bash

pyinstaller --noconfirm --windowed --onefile ^
--name PulseLab_Tuner ^
--icon assets\PulseLab_Tuner.ico ^
--add-data "ui/styles.qss;ui" ^
--add-data "assets/icon.png;assets" ^
main.py
 Algorithm
The tuner uses the YIN algorithm for fundamental frequency detection, providing stable and accurate pitch recognition even in noisy environments.

 Future Improvements
Waveform selection (Sine / Square / Saw)
Recording functionality
Android version
Practice statistics tracking
MIDI support
 Author
Developed by Ahura

 License
This project is released for educational and personal use.
