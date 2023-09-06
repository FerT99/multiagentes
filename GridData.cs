using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.IO;
using System.Text;
using static ChangeColor;
using static Robots;

public class GridData : MonoBehaviour
{
    public GridMaker grid;
    public CameraScript camera;
    public TimeUI text;
    public Robots robot;
    public Step api;
    public ChangeColor change;
    public Robots Robots;
    public TimeUI TimeUI;

    void Start()
    {
        int col_count;
        int row_count;
        api = createGrid();
        if (api != null)
        {
            col_count = api.STEP_LIST[0].COL_COUNT;
            row_count = api.STEP_LIST[0].ROW_COUNT;
            grid.GenerateGrid(col_count, row_count);
            camera.adjustCamera(row_count, col_count);
            text.MoveText(50, 25);
            robot.GenerateRobots(5, api.STEP_LIST[0].START_X, api.STEP_LIST[0].START_Y);
        }
        else
        {
            Debug.LogError("Failed to fetch API data.");
        }

        InvokeRepeating("TaskManager", 0f, .25f);

    }

    public static Step createGrid() 
    {
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://localhost:8585/unity_url");
        request.Method = "POST"; // Set the request method to POST
        request.ContentType = "application/json"; // Set content type to JSON

        string postData = ""; 

        byte[] postDataBytes = Encoding.UTF8.GetBytes(postData);
        request.ContentLength = postDataBytes.Length;

        using (Stream requestStream = request.GetRequestStream())
        {
            requestStream.Write(postDataBytes, 0, postDataBytes.Length);
        }

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();

        StreamReader reader = new StreamReader(response.GetResponseStream());

        string json = reader.ReadToEnd();
        return JsonUtility.FromJson<Step>(json);
    }

    public void TaskManager()
    {
        int col_count = api.STEP_LIST[0].COL_COUNT;
        int row_count = api.STEP_LIST[0].ROW_COUNT;
        List<int> robot_listx = api.STEP_LIST[TimeUI.i].ROBOT_POSX;
        List<int> robot_listy = api.STEP_LIST[TimeUI.i].ROBOT_POSY;

        int x = 0;
        for (int row = 0; row < (row_count*col_count) -1; row += col_count)
        {
            for (int col = 0; col < col_count; col++)
            {
                int key = api.STEP_LIST[TimeUI.i].KNOWN_GRID[row + col];
                change.Color(col, x, key);
            }
            x++;
        }

        Robots.RobotMoveTo(0, robot_listy[0], robot_listx[0]);
        Robots.RobotMoveTo(1, robot_listy[1], robot_listx[1]);
        Robots.RobotMoveTo(2, robot_listy[2], robot_listx[2]);
        Robots.RobotMoveTo(3, robot_listy[3], robot_listx[3]);
        Robots.RobotMoveTo(4, robot_listy[4], robot_listx[4]);
    }
}
