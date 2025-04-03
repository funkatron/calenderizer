#!/usr/bin/env python3
"""
Tests for the calendar generator functionality.
"""

import unittest
import json
import os
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event
from ics_generator import (
    format_tasks,
    calculate_total_hours,
    create_event,
    create_calendar,
    TASK_BUFFER_HOURS
)

class TestCalendarGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.test_tasks = [
            {"hours": 4, "title": "First Task"},
            {"hours": 2, "title": "Second Task"},
            {"hours": 3, "title": "Third Task"}
        ]
        self.test_entry = {
            "date": "2025-04-01",
            "phase": "🔵 Test Phase",
            "start_time": "11:00",
            "tasks": self.test_tasks
        }
        self.timezone = "America/New_York"

    def test_format_tasks(self):
        """Test task formatting with emojis and summary."""
        formatted = format_tasks(self.test_tasks)

        # Check that the summary line is present
        self.assertIn("📅 Total:", formatted)
        self.assertIn("9 hrs + 1.0 hrs buffer = 10.0 hrs", formatted)

        # Check that all tasks are present with correct emojis
        self.assertIn("🎯 4 hrs: First Task", formatted)
        self.assertIn("⚡ 2 hrs: Second Task", formatted)
        self.assertIn("🏁 3 hrs: Third Task", formatted)

    def test_calculate_total_hours(self):
        """Test total hours calculation including buffer time."""
        # Test with multiple tasks
        total = calculate_total_hours(self.test_tasks)
        expected = 9 + (2 * TASK_BUFFER_HOURS)  # 9 hours of tasks + 2 buffers
        self.assertEqual(total, expected)

        # Test with single task (no buffer)
        single_task = [{"hours": 4, "title": "Single Task"}]
        total = calculate_total_hours(single_task)
        self.assertEqual(total, 4)

    def test_create_event(self):
        """Test event creation with correct times and content."""
        event = create_event(self.test_entry, self.timezone)

        # Check event properties
        self.assertIsInstance(event, Event)
        self.assertEqual(event['summary'], "🔵 Test Phase: First Task")

        # Check start time
        tz = pytz.timezone(self.timezone)
        expected_start = tz.localize(datetime(2025, 4, 1, 11, 0))
        self.assertEqual(event['dtstart'].dt, expected_start)

        # Check end time (9 hours of tasks + 2 buffers = 10 hours total)
        expected_end = expected_start + timedelta(hours=10)
        self.assertEqual(event['dtend'].dt, expected_end)

    def test_create_calendar(self):
        """Test calendar creation with multiple events."""
        schedule = [
            self.test_entry,
            {
                "date": "2025-04-02",
                "phase": "🟢 Another Phase",
                "start_time": "11:00",
                "tasks": [{"hours": 4, "title": "Single Task"}]
            }
        ]

        calendar = create_calendar(schedule, self.timezone)

        # Check calendar properties
        self.assertIsInstance(calendar, Calendar)
        self.assertEqual(calendar['version'], '2.0')

        # Check number of events
        events = [comp for comp in calendar.subcomponents if isinstance(comp, Event)]
        self.assertEqual(len(events), 2)

if __name__ == '__main__':
    unittest.main()