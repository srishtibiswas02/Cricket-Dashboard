# Cricket Dashboard Application

A Python application built with Tkinter that provides cricket match analytics and visualizations.

## Features

- Real-time data fetching from Cricbuzz API
- Interactive match statistics and visualizations
- Detailed batting and bowling analysis
- Player statistics and performance metrics
- Match progress tracking and key moments analysis
- Custom match ID input for viewing different matches

## Requirements

- Python 3.6+
- Required packages:
  - tkinter
  - matplotlib
  - numpy
  - requests
  - pillow

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install matplotlib numpy requests pillow
   ```
3. Run the application:
   ```
   python cricket_dashboard.py
   ```

## Usage

1. When the application starts, enter a match ID (default: 115102)
2. The dashboard will load with the match data
3. Use the sidebar to select different views and teams
4. Click "Change Match ID" to switch to a different match
5. Enable auto-refresh to keep the data updated

## Screenshots

![Cricket Dashboard Overview](screenshots/overview.png)

## API Information

This application uses the Cricbuzz API through RapidAPI to fetch match data.

## License

MIT License 