using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using static GridData;

public class TimeUI : MonoBehaviour
{
    public TextMeshProUGUI countText;
    public static int i = 0;
    public GridData GridData;

    public void MoveText(float x, float y)
    {
        countText.transform.position = new Vector3(x, y, 1);
    }

    private void OnEnable()
    {
        TimeManager.OnMinuteChanged += UpdateTime;
    }

    private void OnDisable()
    {
        TimeManager.OnMinuteChanged -= UpdateTime;
    }

    private void UpdateTime()
    {
        int counter = GridData.api.STEP_LIST[i].KNOWN_GRID.Count;
        countText.text = $"{TimeManager.Minute:000}";
        i++;
        if (i == counter) 
        {
            CancelInvoke("TaskManager");
        }

    }
}

