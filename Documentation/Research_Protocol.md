# Research Protocol: Neurofeedback with Fractal Visuals

## Overview
This study develops a closed-loop neurofeedback system that adjusts fractal visual complexity based on real-time EEG measurements of cognitive states (focus, relaxation, engagement). The system synchronizes fractal dimension changes with EEG-derived cognitive markers to guide participants toward desired mental states.

## Methodology
1. **EEG Acquisition**: 
   - EMOTIV EPOC X headset (14 electrodes + 2 references)
   - Electrode placement: AF3/AF4, F3/F4, F7/F8, FC5/FC6, P3/P4, P7/P8, O1/O2
   - Impedance < 5 kΩ
   - 1Hz sampling rate

2. **Cognitive Metrics**:
   - Focus: Cognitive attention level
   - Relaxation: Mental calmness
   - Engagement: Task involvement

3. **Feedback Mechanism**:
   - Command calculation based on cognitive state changes:
     - Increase (1): Metric improved
     - Decrease (-1): Metric declined
     - No change (0)
   - Fractal dimension adjusted by ±0.015 per command

4. **Visual Stimuli**:
   - Mandelbrot fractals with fractal dimension range: 1.11 - 2.0
   - Complexity updated every second

5. **Experimental Design**:
   - Double-blind, sham-controlled trial
   - 5 sessions per participant
   - 5-minute sessions, eyes open
   - Feedback group: Real neurofeedback
   - Sham group: Predefined fractal sequence

## System Architecture
```mermaid
graph LR
A[EEG Headset] --> B(Python Processing)
B --> C[LSL Stream]
C --> D(Unity Visualization)
D --> E[Fractal Display]
E --> A
