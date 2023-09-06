using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChangeColor : MonoBehaviour
{
    public Color Unknown, Clean, Dirty, Trash, Start, Obstacle;
    public Color OffSetUnknown, OffsetClean, OffsetDirty, OffsetTrash, OffsetStart;
    GameObject square;

    public void Color(int x, int y, int flag)
    {
        square = GameObject.Find($"Square {x} {y}");
        var squareRenderer = square.GetComponent<Renderer>();
        var offSet = (x % 2 == 0 && y % 2 != 0) || (x % 2 != 0 && y % 2 == 0);

        switch ((flag)) 
        {
            case (0):
                //yellow/uknown
                squareRenderer.material.SetColor("_Color", Unknown);
                break;
            
            case (2):
                //green/clean
                squareRenderer.material.SetColor("_Color", Clean);
                break;
            
            case (4):
                //purple/start
                squareRenderer.material.SetColor("_Color", Start);
                break;                                                      
            
            case (3):
                //blue/trashbin
                squareRenderer.material.SetColor("_Color", Trash);
                break;

            case (5):
                //obstacles
                squareRenderer.material.SetColor("_Color", Obstacle);
                break;

            default:
                squareRenderer.material.SetColor("_Color", Dirty);
                break;
        }
    }
}