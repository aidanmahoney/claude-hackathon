"""Diagnose the API issues"""

import asyncio
import httpx

async def check_endpoints():
    """Test various possible API endpoints"""

    client = httpx.AsyncClient(timeout=10.0)

    endpoints = [
        "https://static.uwcourses.com/update.json",
        "https://static.uwcourses.com/terms.json",
        "https://static.uwcourses.com/subjects.json",
        "https://static.uwcourses.com/1252/courses.json",
        "https://static.uwcourses.com/1252/COMP%20SCI.json",
        "https://static.uwcourses.com/1252/COMPSCI.json",
        "https://enroll.wisc.edu/api/search/v1",
        "https://public.enroll.wisc.edu/api/search/v1",
    ]

    print("Testing possible API endpoints:\n")

    for url in endpoints:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {url}")
                print(f"  Status: {response.status_code}")

                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:10]}")
                    print(f"  Total keys: {len(data)}")
                elif isinstance(data, list):
                    print(f"  Type: List with {len(data)} items")
                    if data:
                        print(f"  First item keys: {list(data[0].keys())[:10] if isinstance(data[0], dict) else type(data[0])}")
                print()
            else:
                print(f"✗ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {url} - Error: {e}")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(check_endpoints())
