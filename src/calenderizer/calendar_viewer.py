#!/usr/bin/env python3
"""
calendar_viewer.py

This script reads the generated .ics file and creates an HTML view
of the calendar that can be opened in a browser. Supports monthly,
weekly, and daily views.
"""

import os
import argparse
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
from icalendar import Calendar
import pytz

def get_week_dates(date, work_week=True):
    """Get the dates for the week containing the given date."""
    monday = date - timedelta(days=date.weekday())
    return [monday + timedelta(days=i) for i in range(5 if work_week else 7)]

def format_event_time(event):
    """Format the event time consistently."""
    start_time = event['start'].strftime("%I:%M")
    end_time = event['end'].strftime("%I:%M")
    am_pm = event['end'].strftime("%p").lower()
    return f"{start_time}-{end_time}{am_pm}"

def format_event_title(event):
    """Format the event title consistently."""
    summary = event['summary']
    phase = summary.split(':')[0] if ':' in summary else ''
    title = summary.split(':', 1)[1] if ':' in summary else summary
    return phase, title.strip()

def create_daily_view(events_by_date, date):
    """Create HTML for a daily view."""
    html = f"""
        <div class="day-view">
            <div class="day-header">
                <h2>{date.strftime("%A, %B %d, %Y")}</h2>
            </div>
            <div class="timeline">
                <div class="time-axis">
                    {''.join(f'<div class="hour-marker">{h:02d}:00</div>' for h in range(9, 18))}
                </div>
                <div class="events-container">
    """

    if date in events_by_date:
        for event in sorted(events_by_date[date], key=lambda x: x['start']):
            start_time = event['start']
            end_time = event['end']
            duration = (end_time - start_time).total_seconds() / 3600  # hours
            start_hour = start_time.hour + start_time.minute / 60
            top_position = (start_hour - 9) * 60  # Start at 9 AM, convert to pixels (1 hour = 60px)
            height = duration * 60  # Convert hours to pixels (1 hour = 60px)
            phase, title = format_event_title(event)

            html += f"""
                <div class="day-event" style="top: {top_position}px; height: {height}px;">
                    <div class="event-phase">{phase}</div>
                    <div class="event-details">
                        <div class="event-time">{format_event_time(event)}</div>
                        <div class="event-title">{title}</div>
                        <div class="event-description">{event['description']}</div>
                    </div>
                </div>
            """
    else:
        html += '<div class="no-events">No events scheduled</div>'

    html += """
                </div>
            </div>
        </div>
    """
    return html

def create_weekly_view(events_by_date, start_date):
    """Create HTML for a weekly view."""
    week_dates = get_week_dates(start_date)
    html = f"""
        <div class="week">
            <div class="week-header">
                Week of {week_dates[0].strftime("%B %d, %Y")}
            </div>
            <div class="weekdays">
    """

    for date in week_dates:
        day_name = calendar.day_name[date.weekday()]
        today_class = " today" if date == datetime.now().date() else ""

        html += f"""
            <div class="weekday{today_class}">
                <div class="weekday-header">
                    <div class="day-name">{day_name}</div>
                    <div class="date">{date.strftime("%B %d")}</div>
                </div>
        """

        if date in events_by_date:
            for event in sorted(events_by_date[date], key=lambda x: x['start']):
                phase, title = format_event_title(event)
                html += f"""
                    <div class="event" title="{event['description']}">
                        <span class="event-time">{format_event_time(event)}</span>
                        <span class="event-title">{phase} {title}</span>
                    </div>
                """

        html += "</div>"

    html += """
            </div>
        </div>
    """
    return html

def create_monthly_view(events_by_date, year, month):
    """Create HTML for a monthly view."""
    cal_obj = calendar.monthcalendar(year, month)

    html = f"""
        <div class="month">
            <div class="month-header">
                {calendar.month_name[month]} {year}
            </div>
            <div class="weekdays">
                <div>Sun</div>
                <div>Mon</div>
                <div>Tue</div>
                <div>Wed</div>
                <div>Thu</div>
                <div>Fri</div>
                <div>Sat</div>
            </div>
            <div class="days">
    """

    for week in cal_obj:
        for day in week:
            if day == 0:
                html += '<div class="day other-month"></div>'
            else:
                date = datetime(year, month, day).date()
                today_class = " today" if date == datetime.now().date() else ""
                html += f'<div class="day{today_class}">'
                html += f'<div class="day-number">{day}</div>'

                if date in events_by_date:
                    for event in sorted(events_by_date[date], key=lambda x: x['start'])[:3]:  # Show max 3 events
                        phase, title = format_event_title(event)
                        html += f"""
                            <div class="event" title="{event['description']}">
                                <span class="event-time">{format_event_time(event)}</span>
                                <span class="event-title">{title}</span>
                            </div>
                        """
                    if len(events_by_date[date]) > 3:
                        html += f'<div class="more-events">+{len(events_by_date[date]) - 3} more</div>'

                html += '</div>'

    html += """
            </div>
        </div>
    """
    return html

def create_html_calendar(ics_file='project_schedule.ics', view='weekly', date=None):
    """Create an HTML view of the calendar."""
    if not os.path.exists(ics_file):
        print(f"Error: {ics_file} not found. Please run the calendar generator first.")
        return

    # Read the calendar file
    with open(ics_file, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    # Group events by date
    events_by_date = defaultdict(list)
    all_dates = set()
    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            date_key = start.date()
            all_dates.add(date_key)
            events_by_date[date_key].append({
                'start': start,
                'end': component.get('dtend').dt,
                'summary': component.get('summary', ''),
                'description': component.get('description', '')
            })

    # Set default date to first event date if not specified
    if date is None:
        date = min(all_dates)
    elif isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Format current date for display
    current_date_str = date.strftime("%Y-%m-%d %H:%M:%S")

    # Generate appropriate calendar content based on view
    if view == 'daily':
        calendar_content = create_daily_view(events_by_date, date)
    elif view == 'weekly':
        calendar_content = create_weekly_view(events_by_date, date)
    else:  # monthly
        calendar_content = create_monthly_view(events_by_date, date.year, date.month)

    # Create HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Project Calendar</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #fff;
                color: #333;
            }}
            .calendar-container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            /* Weekly view styles */
            .week {{
                margin-bottom: 30px;
            }}
            .week-header {{
                text-align: left;
                font-size: 16px;
                margin-bottom: 10px;
                color: #333;
                font-weight: 500;
                padding: 0 8px;
            }}
            .weekdays {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                border: 1px solid #ddd;
            }}
            .weekday {{
                padding: 12px;
                border-right: 1px solid #ddd;
                min-height: 120px;
            }}
            .weekday:last-child {{
                border-right: none;
            }}
            .weekday-header {{
                padding-bottom: 8px;
                margin-bottom: 8px;
                border-bottom: 1px solid #ddd;
            }}
            /* Daily view styles */
            .day-view {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 20px;
            }}
            .day-header {{
                margin-bottom: 20px;
            }}
            .day-header h2 {{
                margin: 0;
                font-weight: normal;
                color: #333;
            }}
            .timeline {{
                display: flex;
                gap: 20px;
                position: relative;
                margin-top: 20px;
            }}
            .time-axis {{
                width: 60px;
                position: relative;
                height: 540px;  /* 9 hours * 60px */
            }}
            .hour-marker {{
                position: absolute;
                left: 0;
                width: 100%;
                font-size: 12px;
                color: #70757a;
                height: 60px;  /* 1 hour = 60px */
                border-top: 1px solid #eee;
            }}
            .events-container {{
                flex: 1;
                position: relative;
                height: 540px;  /* 9 hours * 60px */
                background: linear-gradient(#eee 1px, transparent 1px);
                background-size: 100% 60px;  /* 1 hour = 60px */
            }}
            .day-event {{
                position: absolute;
                left: 0;
                right: 0;
                display: flex;
                gap: 16px;
                padding: 8px;
                background: #e8f0fe;
                border-radius: 4px;
                border-left: 4px solid #185abc;
                overflow: hidden;
                transition: all 0.2s ease;
            }}
            .day-event:hover {{
                background: #d2e3fc;
                z-index: 100;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .event-phase {{
                font-weight: 500;
                color: #185abc;
                min-width: 100px;
            }}
            .event-details {{
                flex: 1;
                min-width: 0;  /* Allow text truncation */
            }}
            .event-description {{
                margin-top: 8px;
                color: #555;
                font-size: 12px;
            }}
            /* Shared styles */
            .date {{
                font-size: 14px;
                color: #70757a;
            }}
            .day-name {{
                font-weight: 500;
                color: #333;
            }}
            .event {{
                margin: 0 0 8px 0;
                padding: 6px 8px;
                font-size: 12px;
                line-height: 1.4;
                background: #e8f0fe;
                color: #185abc;
                border-radius: 3px;
            }}
            .event:hover {{
                background: #d2e3fc;
            }}
            .event-time {{
                color: #185abc;
                font-weight: 500;
                margin-bottom: 2px;
            }}
            .event-title {{
                color: #333;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .header h1 {{
                color: #333;
                margin: 0 0 5px 0;
                font-size: 20px;
                font-weight: normal;
            }}
            .header p {{
                color: #70757a;
                margin: 0;
                font-size: 13px;
            }}
            .today {{
                background: #e8f0fe;
            }}
            .today .date {{
                color: #185abc;
                font-weight: 500;
            }}
            .no-events {{
                color: #70757a;
                font-style: italic;
                padding: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="calendar-container">
            <div class="header">
                <h1>Project Schedule</h1>
                <p>{current_date_str}</p>
            </div>
            {calendar_content}
        </div>
    </body>
    </html>
    """

    # Write the HTML file
    output_file = 'calendar_view.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Open the file in the default browser
    import webbrowser
    webbrowser.open('file://' + os.path.abspath(output_file))
    print(f"Calendar view opened in your browser: {os.path.abspath(output_file)}")

def main():
    parser = argparse.ArgumentParser(description='Generate a calendar view from an ICS file.')
    parser.add_argument('--view', choices=['daily', 'weekly', 'monthly'], default='weekly',
                      help='Calendar view type (default: weekly)')
    parser.add_argument('--date', help='Date to show (YYYY-MM-DD format)')
    args = parser.parse_args()

    create_html_calendar(view=args.view, date=args.date)

if __name__ == "__main__":
    main()