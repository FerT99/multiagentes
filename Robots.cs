using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robots : MonoBehaviour
{
    public Robot RobotPrefab;

    //generate robots when they are obtained from python server
    public void GenerateRobots(int numRobots, int x, int y)
    {
        for (int i = 0; i < numRobots; i++)
        {
            var createRobot = Instantiate(RobotPrefab, new Vector3(x, y), Quaternion.Euler(0, -90, 90));
            createRobot.name = $"Robot {i}";
        }
    }

    public void RobotMoveTo(int num, int x, int y)
    {
        GameObject Robot = GameObject.Find($"Robot {num}");
        //if robots have been created
        if (Robot != null)
        {
            Vector3 targetPos = new Vector3(x, y, 0);
            Robot.transform.position = targetPos;
        }
    }
}