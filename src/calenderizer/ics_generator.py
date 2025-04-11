#!/usr/bin/env python3
"""
ics_generator.py

This script reads a schedule from an external JSON file (schedule.json)
and generates an iCalendar (.ics) file with individual events for each task.
Each event includes:
  - Date and start time (calculated based on previous tasks)
  - Duration based on task hours
  - Phase (e.g., "🔵 Res/API")
  - Task description and hours

The resulting .ics file can be imported into iCal or any other calendar app.
"""

import argparse
import datetime
import json
import logging
import os
import subprocess
from icalendar import Calendar, Event
import pytz

# Default configuration values
DEFAULT_INPUT_FILE = "schedule.json"
DEFAULT_OUTPUT_FILE = "project_schedule.ics"
DEFAULT_TIMEZONE = "America/New_York"
DEFAULT_TASK_BUFFER_HOURS = 0.5  # 30 minutes
DEFAULT_WORK_HOURS = 8

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert JSON schedule to an iCalendar file.'
    )
    parser.add_argument(
        '-i', '--input', default=DEFAULT_INPUT_FILE,
        help='Path to the input JSON schedule file.'
    )
    parser.add_argument(
        '-o', '--output', default=DEFAULT_OUTPUT_FILE,
        help='Path to the output ICS file.'
    )
    parser.add_argument(
        '-t', '--timezone', default=DEFAULT_TIMEZONE,
        help='Timezone for event conversion.'
    )
    parser.add_argument(
        '--start-time', type=str,
        help='Default start time for events if not provided in JSON (HH:MM format).'
    )
    parser.add_argument(
        '--work-hours', type=int, default=DEFAULT_WORK_HOURS,
        help='Number of work hours per day.'
    )
    parser.add_argument(
        '--buffer-hours', type=float, default=DEFAULT_TASK_BUFFER_HOURS,
        help='Buffer time between tasks in hours.'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Enable verbose logging.'
    )
    return parser.parse_args()

def setup_logging(verbose):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_schedule(filename):
    """
    Load the schedule from a JSON file.

    Expected JSON structure:
      [
        {
          "date": "YYYY-MM-DD",
          "phase": "Phase Icon and Abbreviation",
          "start_time": "HH:MM",  // e.g., "11:00"
          "tasks": [
            {
              "hours": 4,
              "title": "Task description"
            },
            {
              "hours": 2,
              "title": "Task description"
            }
          ]
        },
        ...
      ]
    """
    if not os.path.exists(filename):
        logging.error(f"Error: {filename} not found. Please create the file with your schedule data.")
        return []
    try:
        with open(filename, "r") as f:
            schedule = json.load(f)
        logging.debug(f"Successfully loaded schedule from {filename}")
        return schedule
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON file {filename}: {e}")
        return []

def format_task(task, task_number, total_tasks):
    """
    Format a single task into a readable string with hours and title.
    Uses emojis and formatting to make it more visually engaging.
    """
    # Use different emojis for different task positions
    if task_number == 1:
        emoji = "🎯"  # First task
    elif task_number == total_tasks:
        emoji = "🏁"  # Last task
    else:
        emoji = "⚡"  # Middle tasks

    return f"{emoji} {task['hours']} hrs: {task['title']}"

def create_events(entry, timezone_str, default_start_time=None, buffer_hours=DEFAULT_TASK_BUFFER_HOURS):
    """
    Create iCalendar events for each task in a schedule entry.

    - Creates a separate event for each task
    - Calculates start time based on previous tasks and buffer time
    - Sets the summary to include the phase and task title
    - The description includes the task hours and position
    """
    tz = pytz.timezone(timezone_str)

    # Use provided start_time or default_start_time
    start_time_str = entry.get('start_time') or default_start_time
    if not start_time_str:
        logging.warning(f"No start time provided for {entry['date']}, using default")
        start_time_str = "09:00"  # Fallback default

    base_start_dt = datetime.datetime.strptime(f"{entry['date']} {start_time_str}", "%Y-%m-%d %H:%M")
    base_start_dt = tz.localize(base_start_dt)

    events = []
    current_start = base_start_dt

    for i, task in enumerate(entry['tasks'], 1):
        # Create summary with phase and task
        summary = f"{entry['phase']}: {task['title']}"

        # Create description with task details
        description = format_task(task, i, len(entry['tasks']))

        # Calculate end time for this task
        end_dt = current_start + datetime.timedelta(hours=task['hours'])

        event = Event()
        event.add('summary', summary)
        event.add('description', description)
        event.add('dtstart', current_start)
        event.add('dtend', end_dt)
        event.add('dtstamp', datetime.datetime.now(tz))
        events.append(event)

        # Update start time for next task (including buffer)
        current_start = end_dt + datetime.timedelta(hours=buffer_hours)

    return events

def create_calendar(schedule, timezone_str, default_start_time=None, buffer_hours=DEFAULT_TASK_BUFFER_HOURS):
    """
    Create an iCalendar (Calendar) object by iterating over the schedule entries
    and creating individual events for each task.
    """
    cal = Calendar()
    cal.add('prodid', '-//Geocodio Python Library Project Calendar//')
    cal.add('version', '2.0')

    for entry in schedule:
        events = create_events(entry, timezone_str, default_start_time, buffer_hours)
        for event in events:
            cal.add_component(event)

    return cal

def main():
    args = parse_args()
    setup_logging(args.verbose)

    logging.info(f"Starting calendar generation with configuration:")
    logging.info(f"  Input file: {args.input}")
    logging.info(f"  Output file: {args.output}")
    logging.info(f"  Timezone: {args.timezone}")
    logging.info(f"  Default start time: {args.start_time or 'Not set'}")
    logging.info(f"  Work hours per day: {args.work_hours}")
    logging.info(f"  Buffer between tasks: {args.buffer_hours} hours")

    schedule = load_schedule(args.input)
    if not schedule:
        return

    cal = create_calendar(
        schedule,
        args.timezone,
        args.start_time,
        args.buffer_hours
    )

    output_path = os.path.abspath(args.output)
    with open(args.output, 'wb') as f:
        f.write(cal.to_ical())
    logging.info(f"Calendar exported to {output_path}")

    # Reveal the file in Finder instead of opening it
    subprocess.run(['open', '-R', args.output])

if __name__ == "__main__":
    main()