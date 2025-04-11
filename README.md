# Calenderizer

A Python tool that converts a JSON schedule into an iCalendar (.ics) file, which can be imported into any calendar application.

## Features

- Converts JSON schedule to iCalendar format
- Supports multiple tasks per day
- Calculates task durations and buffer times
- Customizable timezone support
- Configurable work hours and task buffers
- Verbose logging for debugging
- HTML calendar view with daily, weekly, and monthly views

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/calenderizer.git
   cd calenderizer
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

## Usage

### Basic Usage

```bash
python src/calenderizer/ics_generator.py
```

This will use the default settings:
- Input file: `schedule.json`
- Output file: `project_schedule.ics`
- Timezone: America/New_York
- Buffer between tasks: 0.5 hours (30 minutes)

### Advanced Usage

The script supports various command-line options:

```bash
python src/calenderizer/ics_generator.py \
    -i custom_schedule.json \
    -o custom_output.ics \
    -t "Europe/London" \
    --start-time "09:00" \
    --work-hours 8 \
    --buffer-hours 0.25 \
    --verbose
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input JSON schedule file | schedule.json |
| `-o, --output` | Output ICS file | project_schedule.ics |
| `-t, --timezone` | Timezone for events | America/New_York |
| `--start-time` | Default start time (HH:MM) | None |
| `--work-hours` | Work hours per day | 8 |
| `--buffer-hours` | Buffer between tasks (hours) | 0.5 |
| `--verbose` | Enable verbose logging | False |

### Schedule JSON Format

The input JSON file should follow this structure:

```json
[
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
```

### Viewing the Calendar

After generating the ICS file, you can view it in your preferred calendar application or use the built-in HTML viewer:

```bash
python src/calenderizer/calendar_viewer.py --view weekly
```

The HTML viewer supports three view types:
- `daily`: Detailed day view with timeline
- `weekly`: Week view with task summaries
- `monthly`: Month view with task counts

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

```
calenderizer/
├── src/
│   └── calenderizer/
│       ├── __init__.py
│       ├── ics_generator.py
│       └── calendar_viewer.py
├── tests/
│   └── test_calendar_generator.py
├── schedule.json
├── project_schedule.ics
├── calendar_view.html
├── setup.sh
└── README.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.