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
from calenderizer.ics_generator import (
    format_task,
    create_events,
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

    def test_format_task(self):
        """Test task formatting with emojis."""
        # Test first task
        formatted = format_task(self.test_tasks[0], 1, len(self.test_tasks))
        self.assertEqual(formatted, "🎯 4 hrs: First Task")

        # Test middle task
        formatted = format_task(self.test_tasks[1], 2, len(self.test_tasks))
        self.assertEqual(formatted, "⚡ 2 hrs: Second Task")

        # Test last task
        formatted = format_task(self.test_tasks[2], 3, len(self.test_tasks))
        self.assertEqual(formatted, "🏁 3 hrs: Third Task")

    def test_create_events(self):
        """Test event creation with correct times and content."""
        events = create_events(self.test_entry, self.timezone)

        # Check number of events
        self.assertEqual(len(events), 3)

        # Check first event
        first_event = events[0]
        self.assertIsInstance(first_event, Event)
        self.assertEqual(first_event['summary'], "🔵 Test Phase: First Task")
        self.assertEqual(first_event['description'], "🎯 4 hrs: First Task")

        # Check start time
        tz = pytz.timezone(self.timezone)
        expected_start = tz.localize(datetime(2025, 4, 1, 11, 0))
        self.assertEqual(first_event['dtstart'].dt, expected_start)

        # Check end time
        expected_end = expected_start + timedelta(hours=4)
        self.assertEqual(first_event['dtend'].dt, expected_end)

        # Check second event (should start after buffer)
        second_event = events[1]
        expected_second_start = expected_end + timedelta(hours=TASK_BUFFER_HOURS)
        self.assertEqual(second_event['dtstart'].dt, expected_second_start)

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
        self.assertEqual(len(events), 4)  # 3 from first entry + 1 from second entry

if __name__ == '__main__':
    unittest.main()