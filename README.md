# real-time-fractal-neurofeedback-code
first we connect python to our headset for real-time data acquision 
Pandas and Scipy Libraries: Ensure you have pandas and scipy installed for handling CSV and MAT file saving. You can install these with:

bash
pip install pandas scipy  
in python we have : 
Data Recording:

Introduced data_records: A list to hold dictionaries of focus, relaxation, engagement, command, and fractal dimension for each iteration.
Introduced commands_records: A list to store the average command for each second.

File Saving:

At the end of the acquisition loop (when interrupted), the data is saved as CSV files (eeg_data.csv and commands_history.csv).
The data is also stored in a MAT file (eeg_data.mat) suitable for loading into MATLAB or EEGLAB for analysis.

Real-Time Python Code for EEG Data Processing
python
from pylsl import StreamInfo, StreamOutlet  
from pylsl import StreamInfo, StreamOutlet  
import emotiv  
import numpy as np  
import pandas as pd  # For CSV handling  
import scipy.io  # For MAT file handling  
import time  

# Define LSL stream info to communicate with Unity  
info = StreamInfo('EEGData', 'EEG', 1, 100, 'float', 'emotiv12345')  
outlet = StreamOutlet(info)  

# Initialize Emotiv device  
try:  
    headset = emotiv.Emotiv()  
    print("Connected to EMOTIV EPOC X")  
except Exception as e:  
    print(f"Could not connect to Emotiv device: {e}")  
    exit()  

# Initialize variables to hold average commands and previous values  
previous_values = {'focus': 0, 'relaxation': 0, 'engagement': 0}  
commands_history = []  

# Initialize fractal dimension  
fractal_dimension = 1.11  # Starting fractal dimension  
increment_value = 0.015   # Value to adjust the fractal dimension  
print(f"Initial fractal dimension: {fractal_dimension}")  

# Lists to hold data for saving  
data_records = []  # To save in CSV and MAT  
commands_records = []  # To save command history  

# Main loop for data acquisition and processing  
try:  
    while True:  
        # Get EEG data from the Emotiv headset  
        data = headset.dequeue()  
        
        if data is not None:  
            # Extract focus, relaxation, and engagement scores  
            focus = data['focus']  
            relaxation = data['relax']  
            engagement = data['engagement']  

            # Initialize command list for this iteration  
            current_commands = []  

            # Process each cognitive marker  
            for key, current_value in zip(['focus', 'relax', 'engagement'], [focus, relaxation, engagement]):  
                if current_value > previous_values[key]:  # Increased  
                    command = 1  
                elif current_value < previous_values[key]:  # Decreased  
                    command = -1  
                else:  # No change  
                    command = 0  

                current_commands.append(command)  
                previous_values[key] = current_value  # Update previous value for next iteration  
            
            # Calculate the average command for this second  
            avg_command = int(np.mean(current_commands))  
            commands_history.append(avg_command)  
            commands_records.append(avg_command)  # Save command history for later analysis  

            # Send avg_command to Unity via LSL  
            outlet.push_sample([avg_command])  # Send the average command to Unity  
            print(f"Sending avg_command to Unity: {avg_command}")  

            # Adjust the fractal dimension based on the average command  
            if avg_command == 1:  # Increased  
                fractal_dimension += increment_value  
            elif avg_command == -1:  # Decreased  
                fractal_dimension -= increment_value  
            
            # Print current values and updated fractal dimension  
            print(f"Focus: {focus}, Relaxation: {relaxation}, Engagement: {engagement}, Command: {avg_command}, Fractal Dimension: {fractal_dimension:.4f}")  

            # Append data to records for output  
            data_records.append({  
                'focus': focus,  
                'relaxation': relaxation,  
                'engagement': engagement,  
                'command': avg_command,  
                'fractal_dimension': fractal_dimension  
            })  

        # Sleep briefly to allow for other processes; this can be adjusted for responsiveness  
        time.sleep(0.01)  # Sleep for 10 milliseconds  

except KeyboardInterrupt:  
    print("Stopping the acquisition.")  
finally:  
    headset.close()  

    # Save data to CSV  
    df = pd.DataFrame(data_records)  
    df.to_csv('eeg_data.csv', index=False)  
    print("EEG data saved to CSV.")  

    # Save commands to CSV  
    commands_df = pd.DataFrame({'command': commands_records})  
    commands_df.to_csv('commands_history.csv', index=False)  
    print("Commands history saved to CSV.")  

    # Save data to MAT file  
    scipy.io.savemat('eeg_data.mat', { 'data': data_records })  
    print("EEG data saved to MAT file.")
 ------------------------------------------------------------------------------------------------------------

Steps to Set Up LSL in Unity

Download the LSL Unity Plugin:

You can find the LSL Unity plugin on GitHub or the official LSL website. Download and import it into your Unity project.
Create a new C# script:

Create a new C# script called EEGDataReceiver.
Implement the Code:

Use the following code in the EEGDataReceiver.cs script:
EEGDataReceiver.cs
csharp
using System.Collections;  
using UnityEngine;  
using LSL;  // Make sure you have the LSL namespace included  

public class EEGDataReceiver : MonoBehaviour  
{  
    private StreamInlet inlet;  
    private float[] sampleBuffer = new float[1]; // Buffer to hold the incoming data  
    private bool dataAvailable = false;  

    void Start()  
    {  
        // Find the EEGData stream  
        StreamInfo[] streams = LSL.LSL.desc_inlets();  
        foreach (StreamInfo stream in streams)  
        {  
            Debug.Log("Stream available: " + stream);  

            // Check if it is the right stream  
            if (stream.name() == "EEGData" && stream.type() == "EEG")  
            {  
                inlet = new StreamInlet(stream);  
                Debug.Log("Connected to stream: " + stream.name());  
                break;  
            }  
        }  

        if (inlet == null)  
        {  
            Debug.LogError("No EEGData stream found!");  
        }  
    }  

    void Update()  
    {  
        if (inlet != null)  
        {  
            // Pull the sample if available  
            int sampleCount = inlet.pull_sample(sampleBuffer);  
            if (sampleCount > 0)  
            {  
                dataAvailable = true;  
                HandleReceivedData(sampleBuffer[0]);  
            }  
        }  
    }  

    // Handle the received data  
    private void HandleReceivedData(float command)  
    {  
        Debug.Log("Received command from Python: " + command);  

        // Here you can implement what to do with the command  
        // For example:  
        if (command == 1)  
        {  
            Debug.Log("Action: Increase something!");  
        }  
        else if (command == -1)  
        {  
            Debug.Log("Action: Decrease something!");  
        }  
        else  
        {  
            Debug.Log("Action: No change!");  
        }  
    }  
}  
Explanation of the Code
Namespaces:

The LSL namespace is used to access LSL classes and methods.
StreamInlet:

StreamInlet inlet is used to receive data from the LSL stream.
Searching for Stream:

In Start(), it looks for an available stream named EEGData with the type EEG. If found, it initializes the inlet.
Data Retrieval:

In Update(), the script checks for new samples. If a sample is available, it pulls the data into sampleBuffer.
Data Processing:

The HandleReceivedData(float command) method processes the received command and executes actions based on its value (e.g., increasing or decreasing some parameter).
Final Steps
Attach the script: Attach EEGDataReceiver to a GameObject in your scene (e.g., an empty GameObject called EEGReceiver).

Run the Unity Scene: Ensure your Python script is running simultaneously, as it will continuously send data to Unity. Play the scene in Unity, and you should see the logs indicating the commands received from the EEG data.

this is the shader code for Fractal dimension changes in UNITY:
Shader "Explorer/Mandelbrot"  
{  
    Properties  
    {  
        _MainTex ("Texture", 2D) = "white" {}  
        _Area ("Area", vector) = (0, 0, 4, 4)  
        _MaxIter ("Iterations", range(4, 1000)) = 255  
        _Angle ("Angle", range(-3.1415, 3.1415)) = 0  
        _Color ("Color", range(0,1)) = .22  
        _Repeat ("Repeat", float) = 1  
        _Speed ("Speed", float) = 1  
        _FractalDimension ("Fractal Dimension", float) = 1.11 // New property for fractal dimension  
    }  
    SubShader  
    {  
        // No culling or depth  
        Cull Off   
        ZWrite Off   
        ZTest Always  

        Pass  
        {  
            CGPROGRAM  
            #pragma vertex vert  
            #pragma fragment frag  

            #include "UnityCG.cginc"  

            struct appdata  
            {  
                float4 vertex : POSITION;  
                float2 uv : TEXCOORD0;  
            };  

            struct v2f  
            {  
                float2 uv : TEXCOORD0;  
                float4 vertex : SV_POSITION;  
            };  

            v2f vert (appdata v)  
            {  
                v2f o;  
                o.vertex = UnityObjectToClipPos(v.vertex);  
                o.uv = v.uv;  
                return o;  
            }  

            float4 _Area;  
            float _Angle, _MaxIter, _Color, _Repeat, _Speed, _FractalDimension; // Updated to include _FractalDimension  
            sampler2D _MainTex;  

            float2 rot(float2 p, float2 pivot, float a) {  
                float s = sin(a);  
                float c = cos(a);  
                p -= pivot;  
                p = float2(p.x * c - p.y * s, p.x * s + p.y * c);  
                p += pivot;  
                return p;  
            }  

            fixed4 frag (v2f i) : SV_Target  
            {  
                float2 uv = i.uv - .5;  
                uv = abs(uv);  
                float2 c = _Area.xy + uv * _Area.zw;   
                c = rot(c, _Area.xy, _Angle);  

                float r = 20; // Escape radius  
                float r2 = r * r;  

                float2 z = float2(0.0, 0.0), zPrevious;  
                float iter;  
                for (iter = 0; iter < _MaxIter; iter++) {  
                    zPrevious = rot(z, 0, _Time.y);  
                    z = float2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + c;  

                    if (dot(z, z) > r2) break; // if the magnitude squared exceeds r^2, we escape  
                }  

                if (iter >= _MaxIter) return 0;  

                float dist = length(z); // Distance from origin  
                float fracIter = (dist - r) / (r2 - r); // Linear interpolation   
                fracIter = log2(log(dist) / log(r));  

                float m = sqrt(iter / _MaxIter);  
                float4 col = sin(float4(.3, .45, .65, 1) * m * 20) * .5 + .5;  

                if (iter < _FractalDimension)  
                {  
                    col = tex2D(_MainTex, float2(m * _Repeat + _Time.y * _Speed, _Color));  
                }  

                float angle = atan2(z.x, z.y);  
                col *= smoothstep(3, 0, fracIter);  
                col *= 1 + sin(angle * 2 + _Time.y * 4) * .2;  

                return col;  
            }  
            ENDCG  
        }  
    }  
}
this is the code for my navigator in Unity:
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Explorer : MonoBehaviour
{
     public Material mat;
     public Vector2 pos;
     public float scale, angle;

     private Vector2 smoothPos;

     private float smoothScale, smoothAngle;

    private void UpdateShader(){
       smoothPos = Vector2.Lerp(smoothPos, pos, .03f);
        smoothScale = Mathf.Lerp(smoothScale, scale, .03f);
        smoothAngle = Mathf.Lerp(smoothAngle, angle, .03f); 


       float aspect = (float)Screen.width / (float)Screen.height;

        float scaleX = smoothScale;
        float scaleY = smoothScale;

        if (aspect > 1f)
            scaleY /= aspect;
        else 
          scaleX *= aspect;

        mat.SetVector("_Area", new Vector4(smoothPos.x, smoothPos.y, scaleX, scaleY));
        mat.SetFloat("_Angle", smoothAngle);
   }
private void HandleInputs(){

    if (Input.GetKey(KeyCode.KeypadPlus))
     scale *= .995f;
    if (Input.GetKey(KeyCode.KeypadMinus))
     scale *= 1.005f;

     
      if (Input.GetKey(KeyCode.Q))
      angle += .01f;
      if (Input.GetKey(KeyCode.E))
       angle -= .01f;

       Vector2 dir = new Vector2(.01f*scale, 0);
       float s = Mathf.Sin(angle);
       float c = Mathf.Cos(angle);
       dir = new Vector2(dir.x*c, dir.x*s);
    if (Input.GetKey(KeyCode.A))
      pos -= dir;

    if (Input.GetKey(KeyCode.D))
      pos += dir;
     
    dir = new Vector2(-dir.y,dir.x);

    if (Input.GetKey(KeyCode.W))
      pos += dir;

    if (Input.GetKey(KeyCode.S))
      pos -= dir;

}
    void FixedUpdate()
    {
        HandleInputs();
        UpdateShader();
        
    }
}
this is the fractal dimension code:
 Shader "Explorer/mandelbrot"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Area( "Area", vector) = (0, 0, 4, 4)
        _MaxIter("Iterations", range(4, 1000)) =  255
      _Angle("Angle", range(-3.1415, 3.1415)) = 0
        _Color ("Color", range(0,1)) = .22
        _Repeat("Repeat", float) = 1
        _Speed("Speed", float) = 1
    }
    SubShader
    {
        // No culling or depth
        Cull Off ZWrite Off ZTest Always

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }
            
            float4 _Area;
            float _Angle, _MaxIter, _Color, _Repeat, _Speed;
            sampler2D _MainTex;
            
            float2 rot(float2 p, float2 pivot, float a) {
                float s = sin(a);
                float c = cos(a);
                   
                  
                p -= pivot;
                p = float2(p.x*c-p.y*s, p.x*s+p.y*c);
                p += pivot;

                return p;

            }

            fixed4 frag (v2f i) : SV_Target
            {
                float2 uv = i.uv - .5;
                uv = abs(uv);
               float2 c = _Area.xy + uv*_Area.zw; 
               c = rot(c, _Area.xy, _Angle);

               float r = 20; //escapre radius
               float r2 = r * r;

               float2 z, zPrevious;
               float iter;
               for (iter = 0; iter < _MaxIter; iter++) {
                   zPrevious = rot(z, 0, _Time.y);
                   z = float2(z.x*z.x-z.y*z.y, 2*z.x*z.y) + c;

                   if (dot(z, zPrevious) > r) break;
                   
                }
                if (iter > _MaxIter) return 0;
                
                float dist = length(z); //distance from origin
                float fracIter = (dist - r) / (r2 - r); // linear interpolation 
                fracIter = log2( log(dist) / log(r) ) ;

                
                float m = sqrt(iter / _MaxIter);
                float4 col = sin(float4(.3, .45, .65, 1)*m*20)*.5+.5;
                col = tex2D(_MainTex, float2(m*_Repeat + _Time.y*_Speed, _Color));

                float angle = atan2(z.x, z.y);
                
                col *= smoothstep(3, 0, fracIter);
                col *= 1 + sin(angle * 2+_Time.y*4)*.2;
                return col;
            
               
            }
            ENDCG
        }
    }
}

And 
