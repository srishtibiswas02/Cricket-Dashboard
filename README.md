# Cricket Dashboard Application

A comprehensive cricket match dashboard application built with Python and Tkinter that provides real-time match data, statistics, and visualizations.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Code Structure](#code-structure)
6. [Widgets and Components](#widgets-and-components)
7. [API Integration](#api-integration)
8. [Error Handling](#error-handling)

## Overview

The Cricket Dashboard is a desktop application built using Python and Tkinter that allows users to:
- Browse live and recent cricket matches
- Select a specific match using a match ID
- View detailed match statistics and visualizations
- Analyze batting and bowling performances
- Track match progress over time
- Export match data for further analysis

The application fetches data from the Cricbuzz API via RapidAPI and provides a comprehensive interface for cricket fans and analysts.

## Features

- **Match Selection Screen**: Browse and select from live and recent matches
- **Real-time Updates**: Auto-refresh capability to get the latest match data
- **Comprehensive Dashboard**: Multiple tabs for different types of analysis
- **Data Visualization**: Interactive charts and graphs using Matplotlib
- **Player Statistics**: Detailed player performance metrics
- **Match Progress Tracking**: Over-by-over analysis of the match
- **Export Functionality**: Save match data as JSON for external use
- **Error Handling**: Graceful fallback to sample data when API limits are reached

## Installation

### Prerequisites
- Python 3.7+
- Required packages:
  - tkinter
  - matplotlib
  - requests
  - pillow
  - numpy

### Setup
1. Clone the repository:
   ```
   git clone <repository-url>
   cd cricket-dashboard
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python test.py
   ```

## Usage

1. **Selecting a Match**:
   - When the application starts, you'll see the match selection screen
   - Browse through live and recent matches
   - Click on a match card to select it, or
   - Enter a specific match ID in the "Quick Match Access" section
   - Recommended match IDs: 112469, 112462, 112455, 112420, 112402

2. **Dashboard Navigation**:
   - Use the sidebar to switch between teams and views
   - The main content area shows different statistics based on your selection
   - Use the auto-refresh feature to keep data updated
   - Export data or view detailed analysis using the sidebar buttons

3. **Changing Match**:
   - Click "Change Match ID" in the sidebar to select a different match
   - Choose from predefined match IDs or enter a custom one

## Code Structure

The application is built using the `CricketDashboard` class, which contains various methods for:

1. **Initialization and Setup**:
   - `__init__`: Initialize the application and variables
   - `get_match_id`: Display match selection screen and return selected ID
   - `setup_main_dashboard`: Create the main dashboard UI

2. **Data Handling**:
   - `load_matches_data`: Load match data from API or sample data
   - `fetch_data`: Fetch specific match data using a separate thread
   - `process_api_data`: Process raw API data into usable format

3. **UI Creation**:
   - `show_match_selection_screen`: Create the match selection UI
   - `create_header_frame`: Create the application header
   - `create_sidebar`: Create the sidebar with controls
   - `create_main_content`: Create the main content area
   - Various tab creation methods (`create_overview_tab`, etc.)

4. **User Interaction**:
   - `update_dashboard`: Update content based on user selection
   - `change_match_id`: Allow user to change the current match
   - `toggle_auto_refresh`: Enable/disable automatic data refresh

5. **Error Handling and Utilities**:
   - `_use_sample_data`: Provide sample data when API fails
   - `show_toast_notification`: Display temporary notifications
   - `on_close`: Handle application close event

## Widgets and Components

### 1. Windows and Frames

- **Root Window (`tk.Tk`)**:
  - The main application window created in `__init__`
  - Controls the overall application size and title

- **Frames (`tk.Frame`)**:
  - `selection_frame`: Contains the match selection UI
  - `header_frame`: Contains the application header
  - `sidebar_frame`: Contains filtering controls
  - `main_frame`: Contains the main content area
  - Various content frames in each tab

- **LabelFrames (`ttk.LabelFrame`)**:
  - Used to group related controls with a title
  - Example: `quick_access_box` in match selection screen

- **Canvas (`tk.Canvas`)**:
  - Used for scrollable areas in match selection
  - Used for loading animation in the header
  - Example: `live_canvas` for scrollable live matches

### 2. Control Widgets

- **Labels (`tk.Label`)**:
  - Display text and status information
  - Examples: `header_label`, `status_label`, various info labels

- **Buttons (`tk.Button`, `ttk.Button`)**:
  - Trigger actions on click
  - Examples: `load_button`, `refresh_button`, `export_btn`

- **Entry Fields (`tk.Entry`, `ttk.Entry`)**:
  - Allow text input
  - Examples: `quick_id_entry`, `custom_entry` in change match dialog

- **Dropdowns (`ttk.Combobox`)**:
  - Allow selection from a list of options
  - Examples: `team_dropdown`, `view_dropdown`, `id_dropdown`

- **Checkboxes (`ttk.Checkbutton`)**:
  - Toggle boolean options
  - Example: `auto_refresh_check` for auto-refresh control

- **Scrollbars (`ttk.Scrollbar`)**:
  - Enable scrolling in lists and text areas
  - Examples: `live_scrollbar`, various table scrollbars

- **Notebook and Tabs (`ttk.Notebook`, `ttk.Frame`)**:
  - Create tabbed interface for content organization
  - Tabs: `overview_tab`, `batting_tab`, `bowling_tab`, etc.

- **Treeview (`ttk.Treeview`)**:
  - Display tabular data
  - Examples: Partnership tables, player statistics

- **Scrolled Text (`scrolledtext.ScrolledText`)**:
  - Display large amounts of text with scroll capability
  - Example: Match summary text area

### 3. Data Visualization

- **Matplotlib Figures and Axes**:
  - Create data visualizations
  - Example: `fig, ax = plt.subplots()` in various tab creation methods

- **FigureCanvasTkAgg**:
  - Embed Matplotlib charts in Tkinter
  - Example: `canvas = FigureCanvasTkAgg(fig, graph_frame)`

### 4. Custom Dialogs

- **Top Level Windows (`tk.Toplevel`)**:
  - Create modal dialogs
  - Example: Match ID selection dialog in `change_match_id`

- **Message Boxes (`messagebox`)**:
  - Display alerts and information
  - Examples: Error messages, rate limit notifications

## Key Functions and Their Purposes

### Initialization and Setup

- **`__init__(self, root)`**: Initializes the application, sets up variables, colors, and starts the match selection process.

- **`get_match_id(self)`**: Shows the match selection screen and waits for the user to select a match before returning the ID.

- **`setup_main_dashboard(self)`**: Creates the main dashboard interface after a match is selected.

### Data Handling

- **`load_matches_data(self)`**: Fetches available matches from the Cricbuzz API or uses sample data if the API is unavailable.

- **`_use_sample_data(self)`**: Provides realistic sample match data when API access fails or rate limits are reached.

- **`populate_match_selection(self, matches_data)`**: Processes match data and populates the match selection screen.

- **`fetch_data(self)`**: Initiates data fetching for a specific match using a separate thread.

- **`_fetch_data_thread(self)`**: Background thread that makes the API call and processes the response.

- **`process_api_data(self, api_data)`**: Transforms raw API data into a structured format for the dashboard.

### UI Creation Functions

- **`show_match_selection_screen(self)`**: Creates the UI for browsing and selecting matches.

- **`create_match_card(self, parent_frame, match_data)`**: Creates a card displaying match information in the selection screen.

- **`create_header_frame(self)`**: Creates the application header with title and status information.

- **`create_sidebar(self)`**: Creates the sidebar with filtering and control options.

- **`create_main_content(self)`**: Sets up the main content area with tabs.

- **`create_overview_tab(self)`**: Creates the match overview tab with summary charts.

- **`create_batting_tab(self)`**: Creates the batting analysis tab with detailed batting statistics.

- **`create_bowling_tab(self)`**: Creates the bowling analysis tab with detailed bowling statistics.

- **`create_players_tab(self)`**: Creates the player statistics tab with individual player details.

- **`create_progress_tab(self)`**: Creates the match progress tab with over-by-over analysis.

### User Interaction

- **`load_match_from_selection(self, match_id)`**: Loads a match when selected from the match cards.

- **`load_quick_match(self)`**: Loads a match using the ID entered in the quick access field.

- **`update_match_list(self, show_loading=True)`**: Refreshes the list of available matches.

- **`schedule_match_list_refresh(self)`**: Sets up periodic refresh of the match list.

- **`change_match_id(self)`**: Displays a dialog allowing the user to change the match ID.

- **`update_info_panel(self)`**: Updates the match information panel with current match details.

- **`update_dashboard(self, event=None)`**: Updates all dashboard tabs based on the selected team and view.

- **`toggle_auto_refresh(self)`**: Enables or disables automatic data refresh.

- **`export_data(self)`**: Exports match data to a JSON file.

- **`show_detailed_analysis(self)`**: Shows more detailed match analysis.

### Error Handling and Utilities

- **`_update_ui_with_cached_data(self, error_message)`**: Updates UI with cached data when live fetch fails.

- **`_update_ui_with_data(self, processed_data)`**: Updates UI with newly fetched data.

- **`_handle_fetch_error(self, error_message)`**: Handles errors during data fetching.

- **`show_toast_notification(self, message)`**: Displays a temporary notification.

- **`start_loading_animation(self)`** and **`stop_loading_animation(self, success=True)`**: Manage the loading indicator.

- **`_flash_last_updated(self, count=0)`**: Creates a flashing effect on the last updated label.

- **`on_close(self)`**: Handles application close by cleaning up resources.

## API Integration

The application integrates with the Cricbuzz Cricket API via RapidAPI to fetch:

1. **Live and recent matches** (endpoint: `/matches/v1/live`)
2. **Specific match data** (endpoint: `/mcenter/v1/{match_id}/hscard`)

API rate limits are handled gracefully with fallback to sample data when limits are reached.

## Error Handling

The application includes comprehensive error handling:

1. **Network Errors**: Handled with fallback to cached or sample data
2. **API Rate Limits**: Specific handling for 429 errors with user-friendly messages
3. **Data Processing Errors**: Graceful fallback with error messages
4. **Thread Safety**: UI updates safely scheduled on the main thread
5. **Retry Mechanism**: Automatic retry with exponential backoff for temporary failures

---

This README provides a comprehensive overview of the Cricket Dashboard application. For more specific details, refer to the code comments within `test.py`. 