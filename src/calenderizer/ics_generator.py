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

The resulting .ics file (project_schedule.ics) can be imported into iCal or any other calendar app.
"""

import datetime
import json
import os
import subprocess
from icalendar import Calendar, Event
import pytz

# Define the timezone for events.
TIMEZONE = "America/New_York"

# Define buffer time between tasks (in hours)
TASK_BUFFER_HOURS = 0.5  # 30 minutes

def load_schedule(filename="schedule.json"):
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
        print(f"Error: {filename} not found. Please create the file with your schedule data.")
        return []
    with open(filename, "r") as f:
        schedule = json.load(f)
    return schedule

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

def create_events(entry, timezone_str=TIMEZONE):
    """
    Create iCalendar events for each task in a schedule entry.

    - Creates a separate event for each task
    - Calculates start time based on previous tasks and buffer time
    - Sets the summary to include the phase and task title
    - The description includes the task hours and position
    """
    tz = pytz.timezone(timezone_str)
    base_start_dt = datetime.datetime.strptime(f"{entry['date']} {entry['start_time']}", "%Y-%m-%d %H:%M")
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
        current_start = end_dt + datetime.timedelta(hours=TASK_BUFFER_HOURS)

    return events

def create_calendar(schedule, timezone_str=TIMEZONE):
    """
    Create an iCalendar (Calendar) object by iterating over the schedule entries
    and creating individual events for each task.
    """
    cal = Calendar()
    cal.add('prodid', '-//Geocodio Python Library Project Calendar//')
    cal.add('version', '2.0')

    for entry in schedule:
        events = create_events(entry, timezone_str)
        for event in events:
            cal.add_component(event)

    return cal

def main():
    schedule = load_schedule()
    if not schedule:
        return
    cal = create_calendar(schedule)
    output_file = 'project_schedule.ics'
    output_path = os.path.abspath(output_file)
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Calendar exported to {output_path}")

    # Reveal the file in Finder instead of opening it
    subprocess.run(['open', '-R', output_file])

if __name__ == "__main__":
    main()