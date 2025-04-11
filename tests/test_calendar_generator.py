import json
import os
import sys
import tempfile
import pytest
from datetime import datetime
from icalendar import Calendar
from src.calenderizer.ics_generator import (
    load_schedule,
    create_events,
    create_calendar,
    parse_args,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    DEFAULT_TIMEZONE,
    DEFAULT_TASK_BUFFER_HOURS,
    DEFAULT_WORK_HOURS
)

@pytest.fixture
def sample_schedule():
    return [
        {
            "date": "2024-04-01",
            "phase": "🔵 Res/API",
            "start_time": "09:00",
            "tasks": [
                {
                    "hours": 4,
                    "title": "Implement API endpoints"
                },
                {
                    "hours": 2,
                    "title": "Write documentation"
                }
            ]
        }
    ]

@pytest.fixture
def temp_schedule_file(sample_schedule):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_schedule, f)
        return f.name

def test_load_schedule(temp_schedule_file):
    schedule = load_schedule(temp_schedule_file)
    assert len(schedule) == 1
    assert schedule[0]['date'] == "2024-04-01"
    assert len(schedule[0]['tasks']) == 2
    os.unlink(temp_schedule_file)

def test_load_schedule_nonexistent():
    schedule = load_schedule("nonexistent.json")
    assert schedule == []

def test_load_schedule_invalid_json():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json")
        f.close()
        schedule = load_schedule(f.name)
        assert schedule == []
        os.unlink(f.name)

def test_create_events(sample_schedule):
    events = create_events(
        sample_schedule[0],
        timezone_str="UTC",
        default_start_time="09:00",
        buffer_hours=0.5
    )
    assert len(events) == 2

    # Check first event
    event1 = events[0]
    assert event1['summary'] == "🔵 Res/API: Implement API endpoints"
    assert event1['description'].startswith("🎯 4 hrs:")
    assert (event1['dtend'].dt - event1['dtstart'].dt).total_seconds() == 4 * 3600

    # Check second event
    event2 = events[1]
    assert event2['summary'] == "🔵 Res/API: Write documentation"
    assert event2['description'].startswith("🏁 2 hrs:")
    assert (event2['dtend'].dt - event2['dtstart'].dt).total_seconds() == 2 * 3600

def test_create_events_with_default_start_time(sample_schedule):
    # Remove start_time from schedule
    schedule_without_start = sample_schedule[0].copy()
    del schedule_without_start['start_time']

    events = create_events(
        schedule_without_start,
        timezone_str="UTC",
        default_start_time="10:00",
        buffer_hours=0.5
    )
    assert len(events) == 2
    assert events[0]['dtstart'].dt.hour == 10

def test_create_calendar(sample_schedule):
    cal = create_calendar(
        sample_schedule,
        timezone_str="UTC",
        default_start_time="09:00",
        buffer_hours=0.5
    )
    assert isinstance(cal, Calendar)
    assert len(cal.walk('VEVENT')) == 2

def test_parse_args_defaults():
    # Save original argv
    orig_argv = sys.argv
    # Set argv to just the script name to test defaults
    sys.argv = ['ics_generator.py']
    try:
        args = parse_args()
        assert args.input == DEFAULT_INPUT_FILE
        assert args.output == DEFAULT_OUTPUT_FILE
        assert args.timezone == DEFAULT_TIMEZONE
        assert args.work_hours == DEFAULT_WORK_HOURS
        assert args.buffer_hours == DEFAULT_TASK_BUFFER_HOURS
        assert not args.verbose
    finally:
        # Restore original argv
        sys.argv = orig_argv

def test_parse_args_custom():
    # Save original argv
    orig_argv = sys.argv
    # Set custom arguments
    sys.argv = [
        'ics_generator.py',
        '-i', 'custom.json',
        '-o', 'output.ics',
        '-t', 'Europe/London',
        '--start-time', '10:00',
        '--work-hours', '6',
        '--buffer-hours', '0.25',
        '--verbose'
    ]
    try:
        args = parse_args()
        assert args.input == 'custom.json'
        assert args.output == 'output.ics'
        assert args.timezone == 'Europe/London'
        assert args.start_time == '10:00'
        assert args.work_hours == 6
        assert args.buffer_hours == 0.25
        assert args.verbose
    finally:
        # Restore original argv
        sys.argv = orig_argv