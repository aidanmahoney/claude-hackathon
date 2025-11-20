"""Test the official UW Madison enrollment API"""

import asyncio
import httpx
import json

async def test_official_api():
    """Test the official enrollment API"""

    client = httpx.AsyncClient(timeout=10.0)

    print("Testing Official UW Madison Enrollment API\n")

    # Try the search API with parameters
    search_url = "https://enroll.wisc.edu/api/search/v1"

    # Common query parameters for UW Madison's course search
    params = {
        "term": "1252",  # Spring 2025
        "subject": "COMP SCI"
    }

    try:
        print(f"Testing: {search_url}")
        print(f"Params: {params}\n")

        response = await client.get(search_url, params=params)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response structure:")
            print(json.dumps(data, indent=2)[:2000])
        else:
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Try a different API endpoint
    print("\n" + "="*60 + "\n")

    # Test a public course lookup endpoint
    course_url = "https://public.enroll.wisc.edu/api/search/v1"

    try:
        print(f"Testing: {course_url}")
        print(f"Params: {params}\n")

        response = await client.get(course_url, params=params)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response structure:")
            print(json.dumps(data, indent=2)[:2000])
        else:
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_official_api())
