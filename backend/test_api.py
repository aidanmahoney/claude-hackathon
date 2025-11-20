"""Test script for UW Courses API integration"""

import asyncio
from src.api.uw_madison_api import UWMadisonAPI


async def test_api():
    """Test the API client"""
    api = UWMadisonAPI()

    try:
        print("\n" + "="*60)
        print("Testing UW Courses API Integration")
        print("API Endpoint: https://static.uwcourses.com/update.json")
        print("="*60 + "\n")

        # Test 1: Fetch raw API data
        print("1. Fetching raw API data...")
        try:
            data = await api._fetch_courses_data()
            print(f"   ✓ API response received")
            print(f"   Response keys: {list(data.keys())[:10]}")
            print(f"   Total keys in response: {len(data.keys())}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return

        # Test 2: Get current term
        print("\n2. Getting current term...")
        try:
            term = await api.get_current_term()
            print(f"   ✓ Current term: {term}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        # Test 3: Try to fetch a specific course
        print("\n3. Testing course lookup...")
        print("   Enter course details to test:")

        term = input("   Term (press Enter for 1252): ").strip() or "1252"
        subject = input("   Subject (press Enter for 'COMP SCI'): ").strip() or "COMP SCI"
        number = input("   Course Number (press Enter for '400'): ").strip() or "400"

        print(f"\n   Searching for {subject} {number} in term {term}...")

        try:
            enrollment_data = await api.get_enrollment_status(term, subject, number)

            print(f"\n   ✓ Course found!")
            print(f"   Title: {enrollment_data['courseTitle']}")
            print(f"   Sections: {len(enrollment_data['sections'])}")

            for section in enrollment_data['sections']:
                print(f"\n   Section {section['sectionId']}:")
                print(f"     Status: {section['status']}")
                print(f"     Seats: {section['openSeats']}/{section['totalSeats']} open")
                print(f"     Waitlist: {section['waitlistOpen']}/{section['waitlistTotal']} open")
                print(f"     Instructor: {section['instructor']}")

        except ValueError as e:
            print(f"   ✗ Course not found: {e}")
            print(f"\n   This might mean:")
            print(f"   - The course doesn't exist in the current term")
            print(f"   - The API data structure is different than expected")
            print(f"   - The term code is incorrect")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        print("\n" + "="*60)
        print("Test completed")
        print("="*60 + "\n")

    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_api())
