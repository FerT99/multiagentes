using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;


[System.Serializable]
public class RobotData
{
    public string unique_id;
    public int posX;
    public int posY;
    public string type;
    public bool display;
}


public class FetchDataFromAPI : MonoBehaviour
{
    public Transform sceneRoot;
    public GameObject prefabAgent;

    private string apiUrl = "http://127.0.0.1:8585/step";
    private Dictionary<string, GameObject> agentsMap = new Dictionary<string, GameObject>();

    public void OnEnable()
    {
        Timer.OnMinuteChanged += Run;
    }

    public void OnDisable()
    {
        Timer.OnMinuteChanged -= Run;
    }

    void Run()
    {
        StartCoroutine(FetchDataFromPython());
    }

    IEnumerator FetchDataFromPython()
    {
        using (var request = UnityEngine.Networking.UnityWebRequest.Get(apiUrl))
        {
            yield return request.SendWebRequest();

            if (request.result != UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                Debug.Log("Failed to fetch data from API: " + request.error);
                yield break;
            }

            string jsonResponse = request.downloadHandler.text;
            
            // Parse the JSON response and store it in a C# HashMap
            AgentData[] data = JsonConvert.DeserializeObject<AgentData[]>(jsonResponse);

            // Iterate through the data array
            foreach (var agent in data)
            {
                string id = agent.id;
                GameObject agentObj;

                // Check if a GameObject with a Agent component exists for the current id
                if (!agentsMap.ContainsKey(id))
                {
                    // Instantiate a new Agent prefab
                    agentObj = Instantiate(prefabAgent, sceneRoot);

                    // Add the new Agent to the dictionary
                    agentsMap.Add(id, agentObj);

                    // Move to initial position
                    agentObj.transform.position = new Vector3(agent.posX, agent.posY, 0);
                }
                else {
                    agentsMap.TryGetValue(id, out agentObj);
                }
                
                // Set the id for the new Agent
                agentObj.GetComponent<PersonAgent>().id = id;
                agentObj.GetComponent<PersonAgent>().type = agent.type;
                agentObj.GetComponent<PersonAgent>().positionToBe = new int[] { agent.posX, agent.posY };

                // The updates to the new position will be done individually in each agent
            }
        }
    }
}