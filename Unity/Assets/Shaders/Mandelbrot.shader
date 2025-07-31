Shader "Explorer/Mandelbrot"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Area ("Area", Vector) = (0, 0, 4, 4)
        _MaxIter ("Iterations", Range(4, 1000)) = 255
        _Angle ("Angle", Range(-3.1415, 3.1415)) = 0
        _Color ("Color", Range(0, 1)) = 0.22
        _Repeat ("Repeat", Float) = 1
        _Speed ("Speed", Float) = 1
        _FractalDimension ("Fractal Dimension", Range(1.11, 2.0)) = 1.11
    }
    
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100
        
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
            
            float4 _Area;
            float _Angle, _MaxIter, _Color, _Repeat, _Speed, _FractalDimension;
            sampler2D _MainTex;
            
            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }
            
            float2 rotate(float2 p, float2 pivot, float angle)
            {
                float s = sin(angle);
                float c = cos(angle);
                p -= pivot;
                p = float2(p.x * c - p.y * s, p.x * s + p.y * c);
                return p + pivot;
            }
            
            fixed4 frag (v2f i) : SV_Target
            {
                // Adjust for aspect ratio
                float aspect = _ScreenParams.x / _ScreenParams.y;
                float2 uv = i.uv - 0.5;
                uv.x *= aspect;
                
                // Apply fractal area and rotation
                float2 c = _Area.xy + uv * _Area.zw;
                c = rotate(c, _Area.xy, _Angle);
                
                // Mandelbrot iteration
                float2 z = 0;
                float iter;
                const float escapeRadius = 20.0;
                const float escapeRadius2 = escapeRadius * escapeRadius;
                
                for (iter = 0; iter < _MaxIter; iter++)
                {
                    // Rotate previous value for animation
                    float2 zPrev = rotate(z, 0, _Time.y);
                    z = float2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
                    if (dot(z, z) > escapeRadius2) break;
                }
                
                // Inside set → black
                if (iter >= _MaxIter) return 0;
                
                // Calculate coloring parameters
                float dist = length(z);
                float fracIter = log2(log(dist) / log(escapeRadius));
                float m = sqrt(iter / _MaxIter);
                
                // Apply fractal dimension effect
                fixed4 col;
                if (iter < _FractalDimension * 50) // Visual scaling
                {
                    col = tex2D(_MainTex, float2(m * _Repeat + _Time.y * _Speed, _Color));
                }
                else
                {
                    col = sin(float4(0.3, 0.45, 0.65, 1.0) * m * 20.0) * 0.5 + 0.5;
                }
                
                // Final color adjustments
                float angle = atan2(z.x, z.y);
                col *= smoothstep(3.0, 0.0, fracIter);
                col *= 1.0 + sin(angle * 2.0 + _Time.y * 4.0) * 0.2;
                
                return col;
            }
            ENDCG
        }
    }
}
