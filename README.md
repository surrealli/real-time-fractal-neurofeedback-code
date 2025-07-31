# Real-time Neurofeedback System with Fractal Visuals

neurofeedback-fractal-system/
├── Python/
│   ├── eeg_processing.py
│   ├── requirements.txt
│   └── utils.py
├── Unity/
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── EEGDataReceiver.cs
│   │   │   └── FractalController.cs
│   │   ├── Shaders/
│   │   │   └── Mandelbrot.shader
│   │   └── Resources/
│   └── README.md
├── Documentation/
│   ├── Research_Protocol.md
│   └── System_Architecture.png
├── .gitignore


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
The data is also stored in a MAT file (performancematrixtreatmentp1s1.mat/csv) which suitable for loading into MATLAB or EEGLAB for my eeg analysis.
Real-Time Python Code for EEG Data Processing goes like this:
pip install pylsl emotiv numpy  

python
from pylsl import StreamInfo, StreamOutlet  
import emotiv  
import numpy as np  
import pandas as pd  # For CSV handling  
import scipy.io  # For MAT file handling  
import time  

# Define LSL stream info to communicate with Unity  
info = StreamInfo('EEGData', 'EEG', 1, 100, 'float', 'emotiv12345')
#the last line requires your unique emotive headset ID
outlet = StreamOutlet(info)  

# Try connecting to the Emotiv device  
try:  
    headset = emotiv.Emotiv()  
    print("Connected to EMOTIV EPOC X")  
except Exception as e:  
    print(f"Could not connect to Emotiv device: {e}")  
    exit()  

# Initialize variables to hold the previous values  
previous_values = {'focus': 0, 'relaxation': 0, 'engagement': 0}  

# Lists to hold data for saving (optional)  
data_records = []  # To save in CSV and MAT  
commands_records = []  # To save command history  
outlet = StreamOutlet(info)  # Create the LSL Outlet
# Main loop for data acquisition and processing  
try:  
    while True:  
        data = headset.dequeue()  # Get EEG data  

        if data is not None:  
            # Extract focus, relaxation, and engagement scores  
            focus = data['focus']  
            relaxation = data['relax']  
            engagement = data['engagement']  

            # Determine the command based on focus, relaxation, and engagement  
            commands = []  
            current_command = 0  # Default no change  

            if focus > previous_values['focus']:  
                current_command = 1  # Increase  
            elif focus < previous_values['focus']:  
                current_command = -1  # Decrease  
            
            commands.append(current_command)  
            previous_values['focus'] = focus  # Update previous value  

            # If relaxation or engagement also need commands, similar logic can be applied here  

            # Send command to Unity via LSL  
            outlet.push_sample([current_command])  # Send the command to Unity  
            print(f"Sent command: {current_command} to Unity")  

            # Optional: Record data for saving if desired  
            data_records.append({  
                'focus': focus,  
                'relaxation': relaxation,  
                'engagement': engagement,  
                'command': current_command  
            })  

        # Sleep for 1 second before the next data acquisition  
        time.sleep(1)  

except KeyboardInterrupt:  
    print("Stopping the acquisition.")  
finally:  
    headset.close()  

    # Optionally save data to CSV and MAT files if desired  
    df = pd.DataFrame(data_records)  
    df.to_csv('eeg_data.csv', index=False)  
    print("EEG data saved to CSV.")  
    
    scipy.io.savemat('eeg_data.mat', {'data': data_records})  
    print("EEG data saved to MAT file.")
 ------------------------------------------------------------------------------------------------------------

Steps to Set Up LSL in Unity

Download the LSL Unity Plugin:

You can find the LSL Unity plugin on GitHub or the official LSL website. Download and import it into your Unity project.
the url provided blow will guid you with examples for further 
costumizing code in unity and python:
https://github.com/Emotiv/labstreaminglayer/blob/master/examples/unity/readme.md
https://github.com/Emotiv/labstreaminglayer/blob/master/examples/python/readme.md
Create a new C# script:

Create a new C# script called EEGDataReceiver.
Implement the Code:

Use the following code in the EEGDataReceiver.cs script:
using System.Collections;  
using UnityEngine;  
using LSL;  // Make sure you have the LSL namespace included  


subscriber.Connect("tcp://localhost:8001"); // Use appropriate IP connection if required
public class EEGDataReceiver : MonoBehaviour  
{  private Material material; // Reference to the material that has the shader  

    void Start()  
    {  
        // Obtain the material attached to this GameObject  
        material = GetComponent<Renderer>().material;  
    }  

    void UpdateShader()  
    {  
        // Ensure the fractal dimension is up-to-date  
        float fractalDimension = material.GetFloat("_FractalDimension");  
        material.SetFloat("_FractalDimension", fractalDimension);  
        // You can add more shader update functionality here if needed  
    }  
    private StreamInlet inlet;  
    private float[] sampleBuffer = new float[3]; // Buffer to hold incoming data for 3 commands  
    private Material material; // Reference to the material that uses the shader  
    private float fractalDimension = 1.11f; // Default fractal dimension  
    private float lastFocus, lastEngagement, lastRelaxation;  

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

        // Find the material attached to this GameObject  
        material = GetComponent<Renderer>().material;  
    }  

    void Update()  
    {  
        if (inlet != null)  
        {  
            // Pull the sample if available  
            int sampleCount = inlet.pull_sample(sampleBuffer);  
            if (sampleCount > 0)  
            {  
                HandleReceivedData(sampleBuffer);  
            }  
        }  
    }  

    // Handle the received data  
    private void HandleReceivedData(float[] commands)  
    {  
        if (commands.Length >= 3)  
        {  
            float focus = commands[0];  
            float engagement = commands[1];  
            float relaxation = commands[2];  

            // Calculate mean based on new values and last values  
            float meanFocusChange = focus - lastFocus;  
            float meanEngagementChange = engagement - lastEngagement;  
            float meanRelaxationChange = relaxation - lastRelaxation;  

            // Adjust the fractal dimension based on the focus, engagement, and relaxation changes  
            float delta = (meanFocusChange + meanEngagementChange + meanRelaxationChange) / 3.0f;  
            fractalDimension += delta > 0 ? 0.015f : (delta < 0 ? -0.015f : 0);  

            // Clamp the fractal dimension to reasonable limits  
            fractalDimension = Mathf.Clamp(fractalDimension, 1.11f, 2.0f); // Example limits  

            // Set the new fractal dimension to the material  
            material.SetFloat("_FractalDimension", fractalDimension);  

            // Update the last values  
            lastFocus = focus;  
            lastEngagement = engagement;  
            lastRelaxation = relaxation;  

            Debug.Log($"Fractal Dimension Updated: {fractalDimension}, Focus: {focus}, Engagement: {engagement}, Relaxation: {relaxation}");  
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

This combined approach ensures that your Python code properly communicates with Unity via LSL while utilizing the Emotiv headset for real-time neurofeedback processing. Ensure you have the necessary libraries, and test the integration in your environment for the best results.
https://github.com/Emotiv/labstreaminglayer
