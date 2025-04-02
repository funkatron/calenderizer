# Project Calenderizer

A simple tool to convert JSON schedule data into iCalendar (.ics) files that can be imported into calendar applications.

## Prerequisites

- Python 3.12
- Homebrew (for macOS users)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project-calenderizer.git
cd project-calenderizer
```

2. Run the setup script:
```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install required dependencies
- Generate the calendar file from `schedule.json`

## Usage

### Basic Usage

1. Edit the `schedule.json` file with your schedule data:
```json
{
    "events": [
        {
            "summary": "Team Meeting",
            "start": "2024-04-01T10:00:00",
            "end": "2024-04-01T11:00:00",
            "description": "Weekly team sync"
        }
    ]
}
```

2. Run the setup script to generate the calendar:
```bash
./setup.sh
```

3. Import the generated `project_schedule.ics` file into your calendar application.

### Manual Calendar Generation

If you only want to regenerate the calendar without running the full setup:

```bash
source venv/bin/activate
python3 ics-generator.py
```

## Logging

The project includes a logging system with different levels:
- `[debug]` - Step-by-step progress (purple)
- `[info]` - Status updates and completion messages (blue)
- `[warning]` - Potential issues (yellow)
- `[error]` - Error messages (red)

Logs are stored in `app.log` and `setup.log`.

## License

MIT License