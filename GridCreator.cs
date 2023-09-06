using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.IO;
using System.Text;

[System.Serializable]
public class Step
{
    public List<GridCreator> STEP_LIST;
    public int counter;
}

[System.Serializable]
public class GridCreator
{
    public int ROW_COUNT;
    public int COL_COUNT;
    public List<int> ROBOT_POSX;
    public List<int> ROBOT_POSY;
    public int START_X;
    public int START_Y;
    public List<int> KNOWN_GRID;
}
