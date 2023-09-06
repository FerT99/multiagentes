using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Square : MonoBehaviour
{
    public Color baseColor, offSetColor;
    public SpriteRenderer squareRenderer; 

    public void SetColor(bool offSet) {
        squareRenderer.color = offSet ? offSetColor : baseColor; 
    }
}