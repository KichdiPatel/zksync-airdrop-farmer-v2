import requests
import json


def getABI(contract, filename):
    url = f"https://block-explorer-api.mainnet.zksync.io/api?module=contract&action=getabi&address={contract}"
    filepath = f"./ABIs/{filename}.json"

    # Set the headers
    headers = {
        "accept": "application/json",
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = json.loads(response.json()["result"])

        # Write the JSON data to the file, with indentation for readability
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"JSON response saved to {filename}")
    else:
        print(f"Failed to fetch data: {response.status_code}")


getABI("0x8B791913eB07C32779a16750e3868aA8495F5964", "mute")
