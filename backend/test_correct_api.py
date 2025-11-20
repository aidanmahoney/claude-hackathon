"""Test the correct API endpoint"""

import asyncio
import httpx
import json

async def test_correct_api():
    """Test the correct uwcourses.com API"""

    client = httpx.AsyncClient(timeout=10.0)

    print("Testing Correct API Endpoint\n")

    # Test the correct format
    url = "https://static.uwcourses.com/course/COMPSCI_300.json"

    try:
        print(f"Testing: {url}\n")

        response = await client.get(url)
        print(f"Status: {response.status_code}\n")

        if response.status_code == 200:
            data = response.json()
            print("Success! Response structure:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*60 + "\n")

    # Try another course
    url2 = "https://static.uwcourses.com/course/COMPSCI_400.json"

    try:
        print(f"Testing: {url2}\n")

        response = await client.get(url2)
        print(f"Status: {response.status_code}\n")

        if response.status_code == 200:
            data = response.json()
            print("Success! Response structure:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_correct_api())
