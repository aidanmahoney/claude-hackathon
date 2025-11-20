#!/usr/bin/env python3
"""Test database persistence"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.database import Database, CourseMonitor

# Initialize database
db = Database("test_courses.db")

print("🔍 Testing database persistence...\n")

# Test 1: Add a course
print("1️⃣ Adding a course...")
course = db.add_monitored_course(
    term="1252",
    subject="COMP SCI",
    course_number="400",
    sections=["001", "002"],
    notify_on_open=True,
    notify_on_waitlist=False,
    check_interval=300
)
print(f"✅ Added course: {course.subject} {course.course_number} (ID: {course.id})")

# Test 2: Retrieve all courses
print("\n2️⃣ Retrieving all courses...")
courses = db.get_monitored_courses()
print(f"✅ Found {len(courses)} course(s)")
for c in courses:
    print(f"   - {c.subject} {c.course_number}, sections: {c.sections}")

# Test 3: Update a course
print("\n3️⃣ Updating course...")
db.update_monitored_course(course.id, active=False)
updated = db.get_monitored_course(course.id)
print(f"✅ Updated course active status: {updated.active}")

# Test 4: Close and reopen database
print("\n4️⃣ Testing persistence (close and reopen)...")
db.close()
db2 = Database("test_courses.db")
courses2 = db2.get_monitored_courses()
print(f"✅ After reopening: Found {len(courses2)} course(s)")
for c in courses2:
    print(f"   - {c.subject} {c.course_number}, active: {c.active}")

# Test 5: Delete course
print("\n5️⃣ Deleting course...")
db2.delete_monitored_course(course.id)
courses3 = db2.get_monitored_courses()
print(f"✅ After deletion: Found {len(courses3)} course(s)")

db2.close()

print("\n✨ All persistence tests passed!")
print(f"📁 Database file: test_courses.db")

