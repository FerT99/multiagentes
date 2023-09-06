using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static CameraScript;

public class GridMaker : MonoBehaviour
{
    public float width, height;
    public Square SquarePrefab;
    public CameraScript camera;
    public TimeUI text;
    GameObject square;
    public ChangeColor color;  

    public void GenerateGrid(int width, int height)
    {
        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                var createSquare = Instantiate(SquarePrefab, new Vector3( x, y), Quaternion.identity);
                createSquare.name = $"Square {x} {y}";
                var offSet = (x % 2 == 0 && y % 2 != 0) || (x % 2 != 0 && y % 2 == 0);
                createSquare.SetColor(offSet);
            }
        }
    }
    
}