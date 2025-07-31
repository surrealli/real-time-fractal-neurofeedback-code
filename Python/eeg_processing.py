from pylsl import StreamInfo, StreamOutlet
import emotiv
import numpy as np
import pandas as pd
import scipy.io
import time
import sys
from utils import validate_eeg_data

# Configuration
STREAM_NAME = 'EEGData'
STREAM_TYPE = 'EEG'
N_CHANNELS = 3  # Focus, Relaxation, Engagement
SAMPLE_RATE = 1  # 1 Hz
DATA_FORMAT = 'float32'
DEVICE_ID = 'emotiv12345'
SAVE_INTERVAL = 60  # Save data every 60 seconds

class EEGProcessor:
    def __init__(self):
        self.info = StreamInfo(STREAM_NAME, STREAM_TYPE, N_CHANNELS, 
                              SAMPLE_RATE, DATA_FORMAT, DEVICE_ID)
        self.outlet = StreamOutlet(self.info)
        self.previous_values = {'focus': 0, 'relaxation': 0, 'engagement': 0}
        self.data_records = []
        self.session_start = time.time()
        
        try:
            self.headset = emotiv.Emotiv()
            print("✅ Connected to EMOTIV EPOC X")
        except Exception as e:
            print(f"❌ Could not connect to Emotiv device: {e}")
            sys.exit(1)
    
    def calculate_command(self, current, previous):
        if current > previous:
            return 1
        elif current < previous:
            return -1
        return 0
    
    def process_sample(self, data):
        # Extract and validate cognitive scores
        focus = validate_eeg_data(data.get('focus', 0))
        relaxation = validate_eeg_data(data.get('relax', 0))
        engagement = validate_eeg_data(data.get('engagement', 0))
        
        # Calculate commands for each metric
        focus_cmd = self.calculate_command(focus, self.previous_values['focus'])
        relax_cmd = self.calculate_command(relaxation, self.previous_values['relaxation'])
        engage_cmd = self.calculate_command(engagement, self.previous_values['engagement'])
        
        # Send commands to Unity via LSL
        self.outlet.push_sample([focus_cmd, relax_cmd, engage_cmd])
        
        # Record data
        self.data_records.append({
            'timestamp': time.time(),
            'focus': focus,
            'relaxation': relaxation,
            'engagement': engagement,
            'focus_cmd': focus_cmd,
            'relax_cmd': relax_cmd,
            'engage_cmd': engage_cmd
        })
        
        # Update previous values
        self.previous_values = {
            'focus': focus,
            'relaxation': relaxation,
            'engagement': engagement
        }
        
        # Periodic saving
        if time.time() - self.session_start > SAVE_INTERVAL:
            self.save_data()
            self.session_start = time.time()
    
    def save_data(self):
        if self.data_records:
            df = pd.DataFrame(self.data_records)
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            
            # Save to CSV
            csv_file = f"eeg_session_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            
            # Save to MAT
            mat_file = f"eeg_session_{timestamp}.mat"
            scipy.io.savemat(mat_file, {'eeg_data': df.to_dict('list')})
            
            print(f"💾 Session data saved to {csv_file} and {mat_file}")
            self.data_records = []
    
    def run(self):
        print("🚀 Starting EEG data acquisition...")
        try:
            while True:
                data = self.headset.dequeue()
                if data is not None:
                    self.process_sample(data)
                time.sleep(1)  # 1Hz sampling rate
                
        except KeyboardInterrupt:
            print("🛑 Stopping acquisition")
        finally:
            self.headset.close()
            self.save_data()
            print("🔌 EMOTIV device disconnected")

if __name__ == "__main__":
    processor = EEGProcessor()
    processor.run()
