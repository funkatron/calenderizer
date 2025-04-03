# Project Calenderizer

A Python tool that generates iCalendar (.ics) files from JSON input, designed for project planning and task scheduling.

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

The setup script will:
- Create a Python virtual environment
- Install required dependencies
- Generate your calendar file

## Usage

### Basic Usage

1. Run the setup script:
   ```bash
   ./setup.sh
   ```

2. Import the generated `project_schedule.ics` file into your calendar application.

### Manual Calendar Generation

You can also generate the calendar file manually:

```bash
python -m calenderizer.ics_generator
```

### Input JSON Format

Create a JSON file with your project events in the following format:

```json
{
  "events": [
    {
      "date": "2024-03-20",
      "phase": "Planning",
      "start_time": "09:00",
      "tasks": [
        {
          "hours": 2,
          "title": "Project kickoff meeting"
        },
        {
          "hours": 1,
          "title": "Requirements gathering"
        }
      ]
    }
  ]
}
```

## Features

- Automatic buffer time between tasks
- Visual task formatting with emojis
- Support for multiple events and phases
- Configurable start times
- Generates standard iCalendar (.ics) files

## Development

### Running Tests

```bash
python -m unittest tests/test_calendar.py -v
```

## Project Structure

```
project-calenderizer/
├── src/
│   └── calenderizer/
│       ├── __init__.py
│       └── ics_generator.py
├── tests/
│   └── test_calendar.py
├── setup.sh
├── log.sh
├── pyproject.toml
└── README.md
```

## Logging

The project uses a custom logging system with the following levels:
- `[info]` - General information (blue)
- `[warning]` - Warnings (yellow)
- `[error]` - Errors (red)
- `[debug]` - Debug information (purple)
- `[complete]` - Task completion (green)
- `[next]` - Next steps (cyan)

Logs are displayed in the terminal with appropriate colors and timestamps.

## License

This project is licensed under the MIT License - see the LICENSE file for details.