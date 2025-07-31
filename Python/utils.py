def validate_eeg_data(value):
    """Ensure EEG values are within valid range"""
    if not isinstance(value, (int, float)):
        return 0.0
    return max(0.0, min(100.0, float(value)))
