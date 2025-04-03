#!/usr/bin/env python3
"""
ics_generator.py

This script reads a schedule from an external JSON file (schedule.json)
and generates an iCalendar (.ics) file with events for each workday.
Each event includes:
  - Date and start time (assumed to be 11:00)
  - Workday end time calculated based on total task hours plus buffer time
  - Phase (e.g., "🔵 Res/API")
  - A list of tasks with estimated hours

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

def format_tasks(tasks):
    """
    Format tasks into a readable string with hours and titles.
    Uses emojis and formatting to make it more visually engaging.
    """
    formatted_tasks = []
    for i, task in enumerate(tasks, 1):
        # Use different emojis for different task positions
        if i == 1:
            emoji = "🎯"  # First task
        elif i == len(tasks):
            emoji = "🏁"  # Last task
        else:
            emoji = "⚡"  # Middle tasks

        formatted_tasks.append(f"{emoji} {task['hours']} hrs: {task['title']}")

    # Add a summary line at the top
    total_hours = sum(task['hours'] for task in tasks)
    buffer_hours = TASK_BUFFER_HOURS * (len(tasks) - 1) if len(tasks) > 1 else 0
    total_with_buffer = total_hours + buffer_hours

    summary = f"📅 Total: {total_hours} hrs + {buffer_hours} hrs buffer = {total_with_buffer} hrs"
    return f"{summary}\n\n" + "\n".join(formatted_tasks)

def calculate_total_hours(tasks):
    """
    Calculate the total hours from all tasks plus buffer time between tasks.
    """
    total_task_hours = sum(task['hours'] for task in tasks)

    # Calculate buffer time between tasks
    buffer_hours = 0
    if len(tasks) > 1:
        buffer_hours = TASK_BUFFER_HOURS * (len(tasks) - 1)

    return total_task_hours + buffer_hours

def create_event(entry, timezone_str=TIMEZONE):
    """
    Create an iCalendar event for a given schedule entry.

    - Combines the date and start_time to form a localized datetime.
    - Calculates end time based on total task hours plus buffer time.
    - Sets the summary to include the phase and the first task.
    - The description is a concatenation of all tasks with their hours.
    """
    tz = pytz.timezone(timezone_str)
    start_dt = datetime.datetime.strptime(f"{entry['date']} {entry['start_time']}", "%Y-%m-%d %H:%M")
    start_dt = tz.localize(start_dt)

    # Calculate the end datetime based on total task hours plus buffer time
    total_hours = calculate_total_hours(entry['tasks'])
    end_dt = start_dt + datetime.timedelta(hours=total_hours)

    # Create summary with phase and first task
    first_task = entry['tasks'][0]
    summary = f"{entry['phase']}: {first_task['title']}"

    # Create description with all tasks
    description = format_tasks(entry['tasks'])

    event = Event()
    event.add('summary', summary)
    event.add('description', description)
    event.add('dtstart', start_dt)
    event.add('dtend', end_dt)
    event.add('dtstamp', datetime.datetime.now(tz))
    return event

def create_calendar(schedule, timezone_str=TIMEZONE):
    """
    Create an iCalendar (Calendar) object by iterating over the schedule entries.
    """
    cal = Calendar()
    cal.add('prodid', '-//Geocodio Python Library Project Calendar//')
    cal.add('version', '2.0')

    for entry in schedule:
        event = create_event(entry, timezone_str)
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