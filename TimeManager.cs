using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using static TimeUI;

public class TimeManager : MonoBehaviour
{

    public static Action OnMinuteChanged;

    public static int Minute{get; private set;}

    private float minuteToRealTime = .5f;
    private float timer;

    // Start is called before the first frame update
    void Start()
    {
        Minute = 0;
        timer = minuteToRealTime;
    }

    // Update is called once per frame
    void Update() {
        timer -= Time.deltaTime;

        if(timer <= 0)
        {
            Minute++;

            OnMinuteChanged?.Invoke();

            timer = minuteToRealTime;
        } 
    }

}
