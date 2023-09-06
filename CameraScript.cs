using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraScript : MonoBehaviour
{
    public float margin = 10f;
    public float orthoSize;
    public float centerX, centerY;
    ///public TextMeshProUGUI countText;

    public void adjustCamera(float width, float height)
    {
        if (height >= width) 
        {
            orthoSize = (height + 3) / 2;
        }
        else 
        {
            orthoSize = (width + 3) * Screen.height / Screen.width * 0.5f;
        }
        
        centerX = (width - (2 * margin)) * 0.5f;
        centerY = (height - (2 * margin)) * 0.5f;
        Camera.main.orthographicSize = orthoSize;
        transform.localPosition = new Vector3(centerX, centerY, -10f);
    }

}
