using UnityEngine;

public class FractalController : MonoBehaviour
{
    [Header("Fractal Settings")]
    [SerializeField] private Material fractalMaterial;
    [SerializeField] private float minDimension = 1.11f;
    [SerializeField] private float maxDimension = 2.0f;
    [SerializeField] private float stepSize = 0.015f;
    
    private float currentDimension;
    private static readonly int FractalDimension = Shader.PropertyToID("_FractalDimension");
    
    void Start()
    {
        currentDimension = minDimension;
        UpdateShaderDimension();
    }
    
    public void UpdateFractalDimension(int command)
    {
        // Apply command (-1, 0, +1)
        currentDimension += command * stepSize;
        
        // Clamp to valid range
        currentDimension = Mathf.Clamp(currentDimension, minDimension, maxDimension);
        
        UpdateShaderDimension();
    }
    
    private void UpdateShaderDimension()
    {
        if (fractalMaterial != null)
        {
            fractalMaterial.SetFloat(FractalDimension, currentDimension);
            Debug.Log($"🎨 Fractal Dimension Updated: {currentDimension:F3}");
        }
    }
    
    // For manual testing
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.UpArrow))
        {
            UpdateFractalDimension(1);
        }
        else if (Input.GetKeyDown(KeyCode.DownArrow))
        {
            UpdateFractalDimension(-1);
        }
    }
}
