"""Test searching for courses"""

import asyncio
import httpx
import json

async def test_search():
    """Test different search approaches"""

    client = httpx.AsyncClient(timeout=10.0)

    print("Testing Search API\n")

    # Try the UW search API with POST
    search_url = "https://enroll.wisc.edu/api/search/v1"

    search_body = {
        "termCode": "1252",
        "subjects": ["COMP SCI"]
    }

    try:
        print(f"Testing POST: {search_url}")
        print(f"Body: {json.dumps(search_body, indent=2)}\n")

        response = await client.post(search_url, json=search_body)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Success! Got {len(data) if isinstance(data, list) else 'data'}")
            print(json.dumps(data, indent=2)[:2000])
        else:
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*60 + "\n")

    # Try with catalog number
    search_body2 = {
        "termCode": "1252",
        "subjects": ["COMP SCI"],
        "catalogNumber": "400"
    }

    try:
        print(f"Testing POST with catalog number: {search_url}")
        print(f"Body: {json.dumps(search_body2, indent=2)}\n")

        response = await client.post(search_url, json=search_body2)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Success!")
            print(json.dumps(data, indent=2)[:2000])
        else:
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_search())
