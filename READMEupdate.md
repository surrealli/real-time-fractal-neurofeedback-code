# Neurofeedback Fractal System

A closed-loop neurofeedback system that adjusts fractal visual stimuli based on real-time EEG data to enhance cognitive performance through self-regulation.

## Overview

This system implements the methodology described in the research paper "Adjusting Cognitive Abilities Through Self-Regulation Using Fractal Visual Stimuli and EEG Biofeedback". The system:

1. Acquires real-time EEG data from an EMOTIV EPOC X headset
2. Calculates cognitive metrics (focus, relaxation, engagement)
3. Generates commands to adjust fractal dimension of visual stimuli
4. Displays adaptive fractal visuals in Unity
5. Supports both feedback and sham experimental groups

## System Architecture

## EMOTIV EEG Headset → Python (LSL) → Unity (Fractal Visualization)

## Features

- Real-time EEG data acquisition and processing
- Closed-loop adjustment of fractal dimension based on cognitive performance
- Support for both feedback and sham experimental groups
- Data recording in CSV and MAT formats
- Mandelbrot fractal visualization with adjustable complexity
- Session management for multi-participant experiments

## Requirements

### Hardware
- EMOTIV EPOC X EEG headset
- Computer with Bluetooth connectivity

### Software
- Python 3.7+
- Unity 2019.4 or later
- Lab Streaming Layer (LSL) integration

## Installation

### Python Dependencies

```bash
pip install -r python/requirements.txt

## Unity Setup
Create a new Unity project
Import the LSL Unity package from labstreaminglayer
Copy the contents of unity/Assets to your Unity project's Assets folder
Set up the scene:
Create a plane or quad for fractal display
Attach the MandelbrotWithFractalDimension shader to a material
Attach the EEGDataReceiver script to the fractal display object
Attach the Explorer script to a camera or controller object


Usage
Running the System
1- Start the Python acquisition script:
bash

python python/eeg_acquisition.py
python python/eeg_acquisition.py
2- In Unity, configure the EEGDataReceiver component:
Set Participant ID (e.g., "p1")
Set Session Number (1-5)
Toggle Is Sham Group based on experimental condition

3- Play the Unity scene

## Experimental Protocol

Feedback Group:
Fractal dimension adjusts based on cognitive performance
Commands calculated from changes in focus, relaxation, and engagement
Sham Group:
Fractal dimension changes randomly (semi-steady increase pattern)
No actual feedback based on EEG data
Each session runs for 5 minutes. Data is saved to the eeg_data directory.

## Data Output
The system generates two types of output files:

CSV Files (eeg_data_[PARTICIPANT_ID]s[SESSION_NUM].csv):
Timestamp
Cognitive metrics (focus, relaxation, engagement)
Commands (-1, 0, +1)
Average command
Fractal dimension
MAT Files (performancematrixtreatment[PARTICIPANT_ID]s[SESSION_NUM].mat):
Same data in MATLAB-compatible format


### Configuration
Python Script Configuration
python

IS_SHAM_GROUP = False  # True for sham group, False for feedback group
PARTICIPANT_ID = "p1"  # Participant identifier
SESSION_NUM = 1        # Session number (1-5)
SESSION_DURATION = 300 # 5 minutes in seconds

IS_SHAM_GROUP = False  # True for sham group, False for feedback group
PARTICIPANT_ID = "p1"  # Participant identifier
SESSION_NUM = 1        # Session number (1-5)
SESSION_DURATION = 300 # 5 minutes in seconds

## Unity Configuration
Configure the EEGDataReceiver component in Unity:

Participant ID: Unique identifier for the participant
Session Number: Current session number (1-5)
Is Sham Group: Check for sham group, uncheck for feedback group
## License






