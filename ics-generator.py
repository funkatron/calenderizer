#!/usr/bin/env python3
"""
ics_generator.py

This script reads a schedule from an external JSON file (schedule.json)
and generates an iCalendar (.ics) file with events for each workday.
Each event includes:
  - Date and start time (assumed to be 11:00)
  - Workday end time calculated as 7 hours later (i.e. 18:00, including a break)
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

# Define the number of hours in a workday.
WORKDAY_HOURS = 7

def load_schedule(filename="schedule.json"):
    """
    Load the schedule from a JSON file.

    Expected JSON structure:
      [
        {
          "date": "YYYY-MM-DD",
          "phase": "Phase Icon and Abbreviation",
          "tasks": [
            "4 hrs: Task description",
            "2 hrs: Task description"
          ],
          "start_time": "HH:MM"  // e.g., "11:00"
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

def create_event(entry, timezone_str=TIMEZONE):
    """
    Create an iCalendar event for a given schedule entry.

    - Combines the date and start_time to form a localized datetime.
    - Assumes a workday spans 7 hours (11:00 to 18:00).
    - Sets the summary to include the phase and the first task.
    - The description is a concatenation of all tasks.
    """
    tz = pytz.timezone(timezone_str)
    start_dt = datetime.datetime.strptime(f"{entry['date']} {entry['start_time']}", "%Y-%m-%d %H:%M")
    start_dt = tz.localize(start_dt)

    # Calculate the end datetime; adjust as needed.
    # This line should be moved to module scope
    end_dt = start_dt + datetime.timedelta(hours=WORKDAY_HOURS)

    summary = f"{entry['phase']}: {entry['tasks'][0]}"
    description = "\n".join(entry["tasks"])

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