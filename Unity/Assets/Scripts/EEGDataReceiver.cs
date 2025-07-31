using UnityEngine;
using LSL;

public class EEGDataReceiver : MonoBehaviour
{
    private const string StreamName = "EEGData";
    private const string StreamType = "EEG";
    
    private StreamInlet inlet;
    private float[] sampleBuffer = new float[3]; // [focus_cmd, relax_cmd, engage_cmd]
    private FractalController fractalController;
    
    void Start()
    {
        fractalController = GetComponent<FractalController>();
        
        // Resolve EEG stream
        StreamInfo[] streams = LSL.LSL.resolve_stream("name", StreamName, 1, 2.0f);
        
        if (streams.Length > 0)
        {
            inlet = new StreamInlet(streams[0]);
            Debug.Log($"✅ Connected to EEG stream: {streams[0].name()}");
        }
        else
        {
            Debug.LogError($"❌ No EEG stream found with name: {StreamName}");
            enabled = false; // Disable script
        }
    }
    
    void Update()
    {
        if (inlet != null)
        {
            double timestamp = inlet.pull_sample(sampleBuffer, 0.0f);
            if (timestamp > 0)
            {
                ProcessEEGCommands(sampleBuffer);
            }
        }
    }
    
    private void ProcessEEGCommands(float[] commands)
    {
        if (commands.Length >= 3)
        {
            float focusCmd = commands[0];
            float relaxCmd = commands[1];
            float engageCmd = commands[2];
            
            // Calculate average command (-1, 0, or 1)
            float avgCmd = (focusCmd + relaxCmd + engageCmd) / 3f;
            int roundedCmd = Mathf.RoundToInt(avgCmd);
            
            // Update fractal dimension
            fractalController.UpdateFractalDimension(roundedCmd);
            
            Debug.Log($"🧠 Commands - Focus: {focusCmd}, Relax: {relaxCmd}, Engage: {engageCmd} | Avg: {roundedCmd}");
        }
    }
}
