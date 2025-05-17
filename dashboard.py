import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import requests
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk
import io
import threading
from datetime import datetime

class CricketDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Match Dashboard")
        self.root.geometry("1600x900")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize data
        self.match_data = None
        self.cached_data = None
        self.teams = []
        self.selected_team = tk.StringVar()
        self.selected_view = tk.StringVar(value="Overview")
        self.match_selection_done_var = tk.BooleanVar(value=False)
        self.selected_match_id = "117962"  # Default match ID
        
        # Threading control
        self.is_fetching = False
        self.auto_refresh = tk.BooleanVar(value=True)
        self.auto_refresh_interval = 60  # seconds
        self.failed_attempts = 0
        self.max_retry_attempts = 3
        
        # Define colors for theme
        self.colors = {
            "primary": "#113955",
            "secondary": "#8c1c13",
            "accent": "#16363b",
            "bg_light": "#f0f0f0",
            "text": "#333333",
            "text_light": "#ffffff",
            "text_secondary": "#666666",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        
        # Show match selection screen to get match ID
        self.match_id = self.get_match_id()
        
        # Create main dashboard after match is selected
        self.setup_main_dashboard()
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def get_match_id(self):
        """Show match selection screen and return selected match ID"""
        # Show the match selection screen
        self.show_match_selection_screen()
        
        # Create a special mainloop just for the selection screen
        self.root.wait_variable(self.match_selection_done_var)
        
        # Return the selected match ID
        return self.selected_match_id
    
    def setup_main_dashboard(self):
        """Setup the main dashboard after match selection"""
        # Clear any existing widgets from the selection screen
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main frames
        self.create_header_frame()
        self.create_sidebar()
        self.create_main_content()
        
        # Fetch data
        self.fetch_data()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def load_matches_data(self):
        """Load match data from the API or sample JSON file"""
        try:
            # Start loading animation
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Loading match data...")
            
            # Make API call to fetch live matches
            url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
            headers = {
                # "x-rapidapi-key": "4ade6f2361msh57ccf4cb0584770p18e418jsnc58ddc583a78", #not working key(284 id)
                "x-rapidapi-key": "17c4bae87fmsh204730bfc3da945p101869jsn2a8ef0d22e5d", #working key
                # "x-rapidapi-key": "99cf81f013msh29100b8d02b6b9dp161532jsnd6a92c813a77", #working key (secondary)
                "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
            }
            url_recent = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
            headers_recent = {
                "x-rapidapi-key": "17c4bae87fmsh204730bfc3da945p101869jsn2a8ef0d22e5d",
                "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
            }
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response_recent = requests.get(url_recent, headers=headers_recent, timeout=15)
                if response.status_code == 200:
                    matches_data = response.json()
                    matches_data_recent = response_recent.json()
                    self.populate_match_selection(matches_data, matches_data_recent)
                                        
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"Live matches loaded - {datetime.now().strftime('%H:%M:%S')}")
                elif response.status_code == 429:
                    # Handle rate limit specifically
                    self._use_sample_data()
                    
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"API rate limit reached (429). Using sample data instead.")
                    
                    # Show a more informative message
                    if hasattr(self, 'root') and self.root.winfo_exists():
                        messagebox.showinfo(
                            "API Rate Limit", 
                            "You've reached the RapidAPI rate limit for the Cricbuzz API.\n\n"
                            "The application will use sample data for demonstration purposes.\n\n"
                            "Rate limits typically reset after 24 hours."
                        )
                else:
                    # Fall back to sample data if API fails
                    self._use_sample_data()
                    
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"API error ({response.status_code}). Using sample data.")
            except requests.RequestException as e:
                # Handle network errors
                self._use_sample_data()
                
                if hasattr(self, 'status_label'):
                    self.status_label.config(text=f"Network error: {str(e)}. Using sample data.")
                
        except Exception as e:
            # Fall back to sample data on any error
            self._use_sample_data()
            
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Error: {str(e)}. Using sample data.")
            print(f"Error loading matches: {str(e)}")
    
    def _use_sample_data(self):
        """Use sample data as a fallback"""
        # Sample data structure matching the API format
        sample_data = {
            "typeMatches": [
                {
                    "matchType": "International",
                    "seriesMatches": [
                        {
                            "seriesAdWrapper": {
                                "seriesName": "ICC Men's T20 World Cup 2024",
                                "matches": [
                                    {
                                        "matchInfo": {
                                            "matchId": "112469",
                                            "matchDesc": "13th Match, Group C",
                                            "matchFormat": "T20",
                                            "status": "India won by 8 wickets",
                                            "state": "Complete",
                                            "team1": {"teamName": "India"},
                                            "team2": {"teamName": "Ireland"},
                                            "venueInfo": {"ground": "Nassau County International Stadium", "city": "New York"}
                                        },
                                        "matchScore": {
                                            "team1Score": {
                                                "inngs1": {"runs": 147, "wickets": 6, "overs": 20.0}
                                            },
                                            "team2Score": {
                                                "inngs1": {"runs": 150, "wickets": 2, "overs": 15.2}
                                            }
                                        }
                                    },
                                    {
                                        "matchInfo": {
                                            "matchId": "112462", 
                                            "matchDesc": "10th Match, Group D",
                                            "matchFormat": "T20",
                                            "status": "New Zealand won by 4 wickets",
                                            "state": "Complete",
                                            "team1": {"teamName": "Afghanistan"},
                                            "team2": {"teamName": "New Zealand"},
                                            "venueInfo": {"ground": "Providence Stadium", "city": "Guyana"}
                                        },
                                        "matchScore": {
                                            "team1Score": {
                                                "inngs1": {"runs": 129, "wickets": 6, "overs": 20.0}
                                            },
                                            "team2Score": {
                                                "inngs1": {"runs": 130, "wickets": 6, "overs": 18.1}
                                            }
                                        }
                                    },
                                    {
                                        "matchInfo": {
                                            "matchId": "112455", 
                                            "matchDesc": "9th Match, Group B",
                                            "matchFormat": "T20",
                                            "status": "Australia won by 36 runs",
                                            "state": "Complete",
                                            "team1": {"teamName": "Australia"},
                                            "team2": {"teamName": "England"},
                                            "venueInfo": {"ground": "Kensington Oval", "city": "Barbados"}
                                        },
                                        "matchScore": {
                                            "team1Score": {
                                                "inngs1": {"runs": 201, "wickets": 7, "overs": 20.0}
                                            },
                                            "team2Score": {
                                                "inngs1": {"runs": 165, "wickets": 10, "overs": 18.2}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                },
                {
                    "matchType": "League",
                    "seriesMatches": [
                        {
                            "seriesAdWrapper": {
                                "seriesName": "IPL 2024",
                                "matches": [
                                    {
                                        "matchInfo": {
                                            "matchId": "112420",
                                            "matchDesc": "Final",
                                            "matchFormat": "T20",
                                            "status": "Kolkata Knight Riders won by 8 wickets",
                                            "state": "Complete",
                                            "team1": {"teamName": "Sunrisers Hyderabad"},
                                            "team2": {"teamName": "Kolkata Knight Riders"},
                                            "venueInfo": {"ground": "MA Chidambaram Stadium", "city": "Chennai"}
                                        },
                                        "matchScore": {
                                            "team1Score": {
                                                "inngs1": {"runs": 113, "wickets": 10, "overs": 18.3}
                                            },
                                            "team2Score": {
                                                "inngs1": {"runs": 114, "wickets": 2, "overs": 10.3}
                                            }
                                        }
                                    },
                                    {
                                        "matchInfo": {
                                            "matchId": "112402",
                                            "matchDesc": "Qualifier 2",
                                            "matchFormat": "T20",
                                            "status": "Sunrisers Hyderabad won by 35 runs",
                                            "state": "Complete",
                                            "team1": {"teamName": "Rajasthan Royals"},
                                            "team2": {"teamName": "Sunrisers Hyderabad"},
                                            "venueInfo": {"ground": "MA Chidambaram Stadium", "city": "Chennai"}
                                        },
                                        "matchScore": {
                                            "team1Score": {
                                                "inngs1": {"runs": 139, "wickets": 10, "overs": 19.1}
                                            },
                                            "team2Score": {
                                                "inngs1": {"runs": 175, "wickets": 9, "overs": 20.0}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        # Populate the match selection with the sample data
        self.populate_match_selection(sample_data)
    
    def populate_match_selection(self, matches_data, matches_data_recent):
        """Populate the match selection screen with data from the API"""
        
        for widget in self.live_matches_frame.winfo_children():
            widget.destroy()
        for widget in self.recent_matches_frame.winfo_children():
            widget.destroy()
            
        # Process match data for each category
        live_matches = []
        recent_matches = []
        
        # Extract matches from different types
        for match_type in matches_data.get("typeMatches", []):
            type_name = match_type.get("matchType", "")
            
            for series_match in match_type.get("seriesMatches", []):
                if "seriesAdWrapper" in series_match:
                    series_data = series_match["seriesAdWrapper"]
                    series_name = series_data.get("seriesName", "")
                    
                    for match in series_data.get("matches", []):
                        match_info = match.get("matchInfo", {})
                        status = match_info.get("state", "")
                        
                        match_data = {
                            "id": match_info.get("matchId", ""),
                            "series": series_name,
                            "description": match_info.get("matchDesc", ""),
                            "format": match_info.get("matchFormat", ""),
                            "status": match_info.get("status", ""),
                            "state": status,
                            "team1": match_info.get("team1", {}).get("teamName", ""),
                            "team2": match_info.get("team2", {}).get("teamName", ""),
                            "venue": match_info.get("venueInfo", {}).get("ground", ""),
                            "city": match_info.get("venueInfo", {}).get("city", ""),
                            "type": type_name
                        }
                        
                        # Get score data if available
                        if "matchScore" in match:
                            score_data = match["matchScore"]
                            
                            team1_score = score_data.get("team1Score", {})
                            if team1_score and "inngs1" in team1_score:
                                innings1 = team1_score["inngs1"]
                                match_data["team1_score"] = f"{innings1.get('runs', 0)}/{innings1.get('wickets', 0)} ({innings1.get('overs', 0)} ov)"
                            else:
                                match_data["team1_score"] = "Yet to bat"
                                
                            team2_score = score_data.get("team2Score", {})
                            if team2_score and "inngs1" in team2_score:
                                innings2 = team2_score["inngs1"]
                                match_data["team2_score"] = f"{innings2.get('runs', 0)}/{innings2.get('wickets', 0)} ({innings2.get('overs', 0)} ov)"
                            else:
                                match_data["team2_score"] = "Yet to bat"
                        else:
                            match_data["team1_score"] = "No score"
                            match_data["team2_score"] = "No score"
                        
                        # Categorize matches as live or recent
                        if status in ["In Progress", "Live", "Innings Break", "Tea", "Lunch", "Drinks", "Stumps", "Rain"]:
                            live_matches.append(match_data)
        
        # Process recent matches
        for match_type in matches_data_recent.get("typeMatches", []):
            type_name = match_type.get("matchType", "")
            
            for series_match in match_type.get("seriesMatches", []):
                if "seriesAdWrapper" in series_match:
                    series_data = series_match["seriesAdWrapper"]
                    series_name = series_data.get("seriesName", "")
                    
                    for match in series_data.get("matches", []):
                        match_info = match.get("matchInfo", {})
                        status = match_info.get("state", "")
                        
                        match_data = {
                            "id": match_info.get("matchId", ""),
                            "series": series_name,
                            "description": match_info.get("matchDesc", ""),
                            "format": match_info.get("matchFormat", ""),
                            "status": match_info.get("status", ""),
                            "state": status,
                            "team1": match_info.get("team1", {}).get("teamName", ""),
                            "team2": match_info.get("team2", {}).get("teamName", ""),
                            "venue": match_info.get("venueInfo", {}).get("ground", ""),
                            "city": match_info.get("venueInfo", {}).get("city", ""),
                            "type": type_name
                        }
                        
                        # Get score data if available
                        if "matchScore" in match:
                            score_data = match["matchScore"]
                            
                            team1_score = score_data.get("team1Score", {})
                            if team1_score and "inngs1" in team1_score:
                                innings1 = team1_score["inngs1"]
                                match_data["team1_score"] = f"{innings1.get('runs', 0)}/{innings1.get('wickets', 0)} ({innings1.get('overs', 0)} ov)"
                            else:
                                match_data["team1_score"] = "Yet to bat"
                                
                            team2_score = score_data.get("team2Score", {})
                            if team2_score and "inngs1" in team2_score:
                                innings2 = team2_score["inngs1"]
                                match_data["team2_score"] = f"{innings2.get('runs', 0)}/{innings2.get('wickets', 0)} ({innings2.get('overs', 0)} ov)"
                            else:
                                match_data["team2_score"] = "Yet to bat"
                        else:
                            match_data["team1_score"] = "No score"
                            match_data["team2_score"] = "No score"
                        
                        # Categorize matches as live or recent
                        recent_matches.append(match_data)        
                                  
        # Sort matches - live by state, recent by recency
        live_matches.sort(key=lambda x: 0 if x["state"] == "In Progress" else 1)
        
        # Create match cards for live matches
        if live_matches:
            for match in live_matches:
                self.create_match_card(self.live_matches_frame, match)
        else:
            no_matches_label = tk.Label(
                self.live_matches_frame,
                text="No live matches available",
                font=("Arial", 12),
                bg=self.colors["bg_light"],
                fg=self.colors["text"],
                pady=20
            )
            no_matches_label.pack()
        
        # Create match cards for recent matches
        if recent_matches:
            # Show max 10 recent matches
            for match in recent_matches[:10]:
                self.create_match_card(self.recent_matches_frame, match)
        else:
            no_matches_label = tk.Label(
                self.recent_matches_frame,
                text="No recent matches available",
                font=("Arial", 12),
                bg=self.colors["bg_light"],
                fg=self.colors["text"],
                pady=20
            )
            no_matches_label.pack()
    
    def create_match_card(self, parent_frame, match_data):
        """Create a card for a match in the selection screen"""
        # Create card frame
        card_frame = tk.Frame(
            parent_frame, 
            bg="white",
            relief=tk.RIDGE,
            bd=1,
            pady=10,
            padx=10  # Added horizontal padding
        )
        card_frame.pack(fill=tk.X, pady=5)
        
        # Top row with series name and format
        top_row = tk.Frame(card_frame, bg="white")
        top_row.pack(fill=tk.X)
        
        series_label = tk.Label(
            top_row,
            text=match_data["series"],
            font=("Arial", 9),
            bg="white",
            fg="#666666"
        )
        series_label.pack(side=tk.LEFT)
        
        format_label = tk.Label(
            top_row,
            text=match_data["format"],
            font=("Arial", 9, "bold"),
            bg="white",
            fg=self.colors["accent"]
        )
        format_label.pack(side=tk.RIGHT)
        
        # Team names and scores - using grid for better control
        teams_frame = tk.Frame(card_frame, bg="white", pady=5)
        teams_frame.pack(fill=tk.X)
        teams_frame.columnconfigure(0, weight=3)  # Team name column - takes more space
        teams_frame.columnconfigure(1, weight=2)  # Score column - fixed width
        
        # Team 1
        team1_name = tk.Label(
            teams_frame,
            text=match_data["team1"],
            font=("Arial", 11, "bold"),
            bg="white",
            anchor="w",
            justify=tk.LEFT
        )
        team1_name.grid(row=0, column=0, sticky="w", pady=2)
        
        team1_score = tk.Label(
            teams_frame,
            text=match_data.get("team1_score", ""),
            font=("Arial", 11),
            bg="white",
            anchor="e",
            width=30,  # Fixed width to prevent truncation
            justify=tk.RIGHT
        )
        team1_score.grid(row=0, column=1, sticky="e", pady=2)
        
        # Team 2
        team2_name = tk.Label(
            teams_frame,
            text=match_data["team2"],
            font=("Arial", 11, "bold"),
            bg="white",
            anchor="w",
            justify=tk.LEFT
        )
        team2_name.grid(row=1, column=0, sticky="w", pady=2)
        
        team2_score = tk.Label(
            teams_frame,
            text=match_data.get("team2_score", ""),
            font=("Arial", 11),
            bg="white",
            anchor="e",
            width=30,  # Fixed width to prevent truncation
            justify=tk.RIGHT
        )
        team2_score.grid(row=1, column=1, sticky="e", pady=2)
        
        # Match status
        status_frame = tk.Frame(card_frame, bg="white", pady=5)
        status_frame.pack(fill=tk.X)
        
        status_label = tk.Label(
            status_frame,
            text=match_data["status"],
            font=("Arial", 10),
            bg="white",
            fg="#2c3e50" if match_data["state"] != "In Progress" else "#e74c3c"
        )
        status_label.pack(side=tk.LEFT)
        
        # Venue info
        if match_data.get("venue"):
            venue_text = f"{match_data['venue']}, {match_data['city']}" if match_data.get("city") else match_data["venue"]
            venue_label = tk.Label(
                status_frame,
                text=venue_text,
                font=("Arial", 9),
                bg="white",
                fg="#666666"
            )
            venue_label.pack(side=tk.RIGHT)
        
        # Button to select match
        select_button = tk.Button(
            card_frame,
            text="Select Match",
            bg=self.colors["accent"],
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5,
            command=lambda id=match_data["id"]: self.load_match_from_selection(id)
        )
        select_button.pack(pady=(5, 0))
    
    def load_match_from_selection(self, match_id):
        """Load the selected match and close the selection screen"""
        self.selected_match_id = match_id
        self.match_selection_done_var.set(True)  # Signal that selection is done
    
    def load_match_from_entry(self):
        """Load match from manual entry (deprecated but kept for compatibility)"""
        if hasattr(self, 'manual_entry'):
            match_id = self.manual_entry.get().strip()
            if match_id:
                self.match_selection_done_var.set(True)
                self.selected_match_id = match_id
        else:
            self.load_quick_match()
            
    def load_quick_match(self):
        """Load match from quick access entry"""
        if hasattr(self, 'quick_id_entry'):
            match_id = self.quick_id_entry.get().strip()
            if match_id:
                # Set the selected match ID
                self.selected_match_id = match_id
                # Set selection done flag to true to exit waiting loop
                self.match_selection_done_var.set(True)
    
    def show_match_selection_screen(self):
        """Show the match selection screen"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main frame for match selection
        self.selection_frame = tk.Frame(self.root, bg=self.colors["bg_light"])
        self.selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(self.selection_frame, bg=self.colors["primary"], pady=15)
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(
            header_frame, 
            text="Cricket Dashboard - Match Selection",
            font=("Arial", 18, "bold"),
            bg=self.colors["primary"],
            fg=self.colors["text_light"]
        )
        header_label.pack()
        
        # Add direct match ID entry at the top - more prominent position
        direct_access_frame = tk.Frame(self.selection_frame, bg=self.colors["bg_light"], padx=20, pady=15)
        direct_access_frame.pack(fill=tk.X)
        
        # Add a labelframe to make it stand out
        quick_access_box = ttk.LabelFrame(direct_access_frame, text="Quick Match Access")
        quick_access_box.pack(fill=tk.X, pady=5)
        
        quick_access_content = tk.Frame(quick_access_box, bg=self.colors["bg_light"], padx=10, pady=10)
        quick_access_content.pack(fill=tk.X)
        
        tk.Label(
            quick_access_content,
            text="Enter Match ID:",
            font=("Arial", 12, "bold"),
            bg=self.colors["bg_light"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.quick_id_entry = tk.Entry(quick_access_content, width=15, font=("Arial", 12))
        self.quick_id_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add a suggestion label
        suggestion_label = tk.Label(
            quick_access_content,
            text="Try IDs: 112469, 112462, 112455, 112420, 112402",
            font=("Arial", 10, "italic"),
            fg=self.colors["text_secondary"],
            bg=self.colors["bg_light"]
        )
        suggestion_label.pack(side=tk.LEFT, padx=(0, 20))
        
        load_button = tk.Button(
            quick_access_content,
            text="Load Match",
            bg=self.colors["accent"],
            fg=self.colors["text_light"],
            font=("Arial", 12, "bold"),
            padx=15,
            pady=5,
            command=self.load_quick_match
        )
        load_button.pack(side=tk.RIGHT)
        
        # Main content frame with two columns
        content_frame = tk.Frame(self.selection_frame, bg=self.colors["bg_light"], padx=20, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Live Matches
        live_frame = tk.Frame(content_frame, bg=self.colors["bg_light"], relief=tk.RIDGE, bd=1)
        live_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        # Title for Live Matches
        live_title_frame = tk.Frame(live_frame, bg=self.colors["accent"], padx=10, pady=5)
        live_title_frame.pack(fill=tk.X)
        
        tk.Label(
            live_title_frame,
            text="Live Matches",
            font=("Arial", 14, "bold"),
            bg=self.colors["accent"],
            fg=self.colors["text_light"]
        ).pack(anchor="w")
        
        # Create scrollable area for live matches
        live_canvas = tk.Canvas(live_frame, bg=self.colors["bg_light"])
        live_scrollbar = ttk.Scrollbar(live_frame, orient="vertical", command=live_canvas.yview)
        
        self.live_matches_frame = tk.Frame(live_canvas, bg=self.colors["bg_light"])
        
        # Make sure the live matches frame has a fixed width equal to the canvas
        def configure_live_frame(event):
            # Update scrollregion to include all items
            live_canvas.configure(scrollregion=live_canvas.bbox("all"))
            # Set the frame width to match the canvas width minus padding
            canvas_width = event.width
            live_canvas.itemconfig(live_frame_id, width=canvas_width)
            
        self.live_matches_frame.bind("<Configure>", configure_live_frame)
        
        # Create the window with the frame - store the window ID for later use
        live_frame_id = live_canvas.create_window((0, 0), window=self.live_matches_frame, anchor="nw", width=live_canvas.winfo_width())
        
        # Configure the canvas to expand and fill
        live_canvas.configure(yscrollcommand=live_scrollbar.set)
        live_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        live_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Configure canvas to update width when resized
        def on_live_canvas_configure(event):
            canvas_width = event.width
            live_canvas.itemconfig(live_frame_id, width=canvas_width)
            
        live_canvas.bind('<Configure>', on_live_canvas_configure)
        
        # Right column - Recent Matches
        recent_frame = tk.Frame(content_frame, bg=self.colors["bg_light"], relief=tk.RIDGE, bd=1)
        recent_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        # Title for Recent Matches
        recent_title_frame = tk.Frame(recent_frame, bg=self.colors["accent"], padx=10, pady=5)
        recent_title_frame.pack(fill=tk.X)
        
        tk.Label(
            recent_title_frame,
            text="Recent Matches",
            font=("Arial", 14, "bold"),
            bg=self.colors["accent"],
            fg=self.colors["text_light"]
        ).pack(anchor="w")
        
        # Create scrollable area for recent matches
        recent_canvas = tk.Canvas(recent_frame, bg=self.colors["bg_light"])
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=recent_canvas.yview)
        
        self.recent_matches_frame = tk.Frame(recent_canvas, bg=self.colors["bg_light"])
        
        # Make sure the recent matches frame has a fixed width equal to the canvas
        def configure_recent_frame(event):
            # Update scrollregion to include all items
            recent_canvas.configure(scrollregion=recent_canvas.bbox("all"))
            # Set the frame width to match the canvas width minus padding
            canvas_width = event.width
            recent_canvas.itemconfig(frame_id, width=canvas_width)
            
        self.recent_matches_frame.bind("<Configure>", configure_recent_frame)
        
        # Create the window with the frame - store the window ID for later use
        frame_id = recent_canvas.create_window((0, 0), window=self.recent_matches_frame, anchor="nw", width=recent_canvas.winfo_width())
        
        # Configure the canvas to expand and fill
        recent_canvas.configure(yscrollcommand=recent_scrollbar.set)
        recent_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Configure canvas to update width when resized
        def on_recent_canvas_configure(event):
            canvas_width = event.width
            recent_canvas.itemconfig(frame_id, width=canvas_width)
            
        recent_canvas.bind('<Configure>', on_recent_canvas_configure)
        
        # Manual entry section
        manual_frame = tk.Frame(self.selection_frame, bg=self.colors["bg_light"], pady=15)
        manual_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20)
        
        # Add refresh button
        refresh_button = tk.Button(
            manual_frame,
            text="Refresh Matches",
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            font=("Arial", 11),
            padx=10,
            command=lambda: self.update_match_list(True)
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(
            self.selection_frame,
            text="Loading match data...",
            font=("Arial", 10),
            bg=self.colors["bg_light"],
            fg=self.colors["text"],
            pady=5
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20)
        
        # Load match data
        self.load_matches_data()
        
        # Schedule periodic refresh (every 5 minutes)
        self.match_list_refresh_job = self.root.after(300000, self.schedule_match_list_refresh)
    
    def on_close(self):
        """Handle window close event"""
        # Cancel any pending animations or timers
        if hasattr(self, 'loading_animation_id') and self.loading_animation_id:
            self.root.after_cancel(self.loading_animation_id)
            
        # Cancel match list refresh timer if it exists
        if hasattr(self, 'match_list_refresh_job') and self.match_list_refresh_job:
            self.root.after_cancel(self.match_list_refresh_job)
            self.match_list_refresh_job = None
            
        # Close the window
        self.root.destroy()
    
    def update_match_list(self, show_loading=True):
        """Fetch and update the available matches"""
        # Show loading indicator if requested
        if show_loading and hasattr(self, 'status_label'):
            self.status_label.config(text="Refreshing live matches...")
            self.root.update()
            
        # Clear previous content
        if hasattr(self, 'live_matches_frame'):
            for widget in self.live_matches_frame.winfo_children():
                widget.destroy()
        
        if hasattr(self, 'recent_matches_frame'):
            for widget in self.recent_matches_frame.winfo_children():
                widget.destroy()
        
        # Reload match data - this will fetch from API or use fallback
        self.load_matches_data()
        
        # Visual feedback after refresh
        if show_loading and hasattr(self, 'status_label'):
            self.status_label.config(text=f"Matches refreshed at {datetime.now().strftime('%H:%M:%S')}")
            
            # Create blinking effect for user feedback
            def blink_status(count=0):
                if count < 4:  # Blink 2 times
                    if count % 2 == 0:
                        self.status_label.config(fg=self.colors["accent"])
                    else:
                        self.status_label.config(fg=self.colors["text"])
                    self.root.after(250, lambda: blink_status(count + 1))
                else:
                    self.status_label.config(fg=self.colors["text"])
            
            # Start blinking effect
            blink_status()
    
    def schedule_match_list_refresh(self):
        """Schedule periodic refresh of the match list"""
        # Only refresh if selection screen is visible
        if hasattr(self, 'selection_frame') and self.selection_frame.winfo_ismapped():
            self.update_match_list(show_loading=False)
            
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Match list auto-refreshed at {datetime.now().strftime('%H:%M:%S')}")
            
            # Schedule the next refresh after 5 minutes (300000 ms)
            self.match_list_refresh_job = self.root.after(300000, self.schedule_match_list_refresh)
    
    def create_header_frame(self):
        """Create the header frame with title and refresh button"""
        header_frame = tk.Frame(self.root, bg="#113955", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="Cricket Match Analytics Dashboard", 
            font=("Arial", 16, "bold"),
            bg="#113955",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Right side frame for controls
        controls_frame = tk.Frame(header_frame, bg="#113955")
        controls_frame.pack(side=tk.RIGHT, padx=10)
        
        # Loading indicator
        self.loading_indicator = tk.Canvas(controls_frame, width=20, height=20, bg="#113955", highlightthickness=0)
        self.loading_indicator.pack(side=tk.RIGHT, padx=5)
        self.loading_indicator.create_oval(2, 2, 18, 18, outline="#ffffff", width=2, fill="#3498db", tags="loading")
        
        # Refresh button
        refresh_btn = ttk.Button(
            controls_frame,
            text="Refresh Data",
            command=self.fetch_data
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Status: Ready")
        status_label = tk.Label(
            controls_frame,
            textvariable=self.status_var,
            bg="#113955",
            fg="white"
        )
        status_label.pack(side=tk.RIGHT, padx=5)
        
        # Add last updated time
        self.last_updated_var = tk.StringVar(value="Last updated: Never")
        last_updated_label = tk.Label(
            controls_frame,
            textvariable=self.last_updated_var,
            bg="#113955",
            fg="white"
        )
        last_updated_label.pack(side=tk.RIGHT, padx=5)
        
        # Initialize loading animation
        self.loading_animation_id = None
        self.loading_angle = 0
        
    def start_loading_animation(self):
        """Start the loading animation"""
        # Cancel any existing animation
        if self.loading_animation_id:
            self.root.after_cancel(self.loading_animation_id)
            
        # Reset loading indicator to green
        self.loading_indicator.itemconfig("loading", fill="#2ecc71")
        
        # Start animation
        self._animate_loading()
        
    def _animate_loading(self):
        """Animate the loading indicator"""
        # Update angle
        self.loading_angle = (self.loading_angle + 10) % 360
        
        # Draw arc
        self.loading_indicator.delete("arc")
        self.loading_indicator.create_arc(
            2, 2, 18, 18, 
            start=self.loading_angle, 
            extent=120, 
            outline="", 
            fill="#ffffff",
            tags="arc"
        )
        
        # Schedule next animation frame
        self.loading_animation_id = self.root.after(50, self._animate_loading)
        
    def stop_loading_animation(self, success=True):
        """Stop the loading animation"""
        # Cancel animation
        if self.loading_animation_id:
            self.root.after_cancel(self.loading_animation_id)
            self.loading_animation_id = None
            
        # Update indicator color based on success
        self.loading_indicator.delete("arc")
        
        if success is None:
            # Yellow for warning (using cached data)
            self.loading_indicator.itemconfig("loading", fill="#f39c12")
        else:
            # Green for success, red for error
            self.loading_indicator.itemconfig("loading", fill="#2ecc71" if success else "#e74c3c")
    
    def create_sidebar(self):
        """Create the sidebar with filter options"""
        sidebar_frame = tk.Frame(self.root, bg="#2c3e50", width=200)
        sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, expand=False)
        
        # Make sidebar fixed width
        sidebar_frame.pack_propagate(False)
        
        # Title
        sidebar_title = tk.Label(
            sidebar_frame,
            text="Filters & Controls",
            font=("Arial", 12, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10
        )
        sidebar_title.pack(fill=tk.X, padx=10, pady=10)
        
        # Match ID button - NEW
        match_id_button = ttk.Button(
            sidebar_frame,
            text=f"Change Match ID ({self.match_id})",
            command=self.change_match_id
        )
        match_id_button.pack(fill=tk.X, padx=10, pady=10)
        
        # Team selection
        team_label = tk.Label(
            sidebar_frame,
            text="Select Team:",
            bg="#2c3e50",
            fg="white",
            anchor="w"
        )
        team_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.team_dropdown = ttk.Combobox(
            sidebar_frame,
            textvariable=self.selected_team,
            state="readonly"
        )
        self.team_dropdown.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.team_dropdown.bind("<<ComboboxSelected>>", self.update_dashboard)
        
        # View selection
        view_label = tk.Label(
            sidebar_frame,
            text="Select View:",
            bg="#2c3e50",
            fg="white",
            anchor="w"
        )
        view_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        views = ["Overview", "Batting Analysis", "Bowling Analysis", "Player Stats", "Match Progress"]
        self.view_dropdown = ttk.Combobox(
            sidebar_frame,
            textvariable=self.selected_view,
            values=views,
            state="readonly"
        )
        self.view_dropdown.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.view_dropdown.bind("<<ComboboxSelected>>", self.update_dashboard)
        
        # Additional controls
        refresh_frame = ttk.LabelFrame(sidebar_frame, text="Data Controls", padding=10)
        refresh_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Auto-refresh checkbox
        auto_refresh_check = ttk.Checkbutton(
            refresh_frame,
            text=f"Auto-refresh ({self.auto_refresh_interval}s)",
            variable=self.auto_refresh,
            command=self.toggle_auto_refresh
        )
        auto_refresh_check.pack(fill=tk.X, pady=5)
        
        export_btn = ttk.Button(
            refresh_frame,
            text="Export Data",
            command=self.export_data
        )
        export_btn.pack(fill=tk.X, pady=5)
        
        analyze_btn = ttk.Button(
            refresh_frame,
            text="Detailed Analysis",
            command=self.show_detailed_analysis
        )
        analyze_btn.pack(fill=tk.X, pady=5)
        
        # Empty space
        spacer = tk.Frame(sidebar_frame, bg="#2c3e50")
        spacer.pack(fill=tk.BOTH, expand=True)
        
        # Version info
        version_label = tk.Label(
            sidebar_frame,
            text="v1.0.0",
            bg="#2c3e50",
            fg="#7f8c8d",
            anchor="e"
        )
        version_label.pack(fill=tk.X, padx=10, pady=10)
    
    def create_main_content(self):
        """Create the main content area"""
        # Main content
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        # Match info panel
        info_frame = tk.Frame(self.main_frame, bg="#f0f0f0", pady=10)
        info_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        # Match title
        self.match_title_var = tk.StringVar(value="Loading match information...")
        match_title = tk.Label(
            info_frame, 
            textvariable=self.match_title_var,
            font=("Arial", 14, "bold"),
            wraplength=800,
            justify=tk.CENTER
        )
        match_title.pack(fill=tk.X, pady=(0, 10))
        
        # Match status and last updated (Right aligned)
        status_frame = tk.Frame(info_frame, bg="#f0f0f0")
        status_frame.pack(fill=tk.X)
        
        self.status_display_var = tk.StringVar(value="Status: Loading...")
        status_display_label = tk.Label(status_frame, textvariable=self.status_display_var, font=("Arial", 12))
        status_display_label.pack(side=tk.LEFT)
        
        # Content area
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Overview tab
        self.overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_tab, text="Match Overview")
        
        # Batting tab
        self.batting_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batting_tab, text="Batting Analysis")
        
        # Bowling tab
        self.bowling_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bowling_tab, text="Bowling Analysis")
        
        # Players tab
        self.players_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.players_tab, text="Player Stats")
        
        # Progress tab
        self.progress_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_tab, text="Match Progress")
        
        # Footer with notes
        footer = tk.Frame(self.main_frame, bg="#f0f0f0", height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        note_label = tk.Label(
            footer,
            text="Data provided by Cricket API. Refresh for latest updates.",
            fg="#7f8c8d",
            bg="#f0f0f0"
        )
        note_label.pack(side=tk.RIGHT, padx=20, pady=5)
    
    def fetch_data(self):
        """Fetch data from the API using a separate thread"""
        if self.is_fetching:
            return  # Prevent multiple concurrent fetches
            
        self.is_fetching = True
        self.status_var.set("Status: Fetching data...")
        self.start_loading_animation()
        
        # Start a new thread for the API call
        fetch_thread = threading.Thread(target=self._fetch_data_thread)
        fetch_thread.daemon = True  # Make sure thread doesn't prevent app from closing
        fetch_thread.start()
    
    def _fetch_data_thread(self):
        """Background thread function for fetching data"""
        try:
            # Make the API call with the user-provided match ID
            url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{self.match_id}/hscard"
            headers = {
                # "x-rapidapi-key": "4ade6f2361msh57ccf4cb0584770p18e418jsnc58ddc583a78", #not working key(284 id)
                "x-rapidapi-key": "17c4bae87fmsh204730bfc3da945p101869jsn2a8ef0d22e5d", #working key
                # "x-rapidapi-key": "99cf81f013msh29100b8d02b6b9dp161532jsnd6a92c813a77", #working key (secondary)
                "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, timeout=10)  # Add timeout
            
            if response.status_code == 429:
                # Handle rate limit exceeded
                error_msg = "API rate limit exceeded (429). Try again later."
                self.root.after(0, lambda: messagebox.showinfo(
                    "API Rate Limit", 
                    "You've reached the RapidAPI rate limit for the Cricbuzz API.\n\n"
                    "The application will use cached data if available.\n\n"
                    "Rate limits typically reset after 24 hours."
                ))
                raise Exception(error_msg)
            elif response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
                
            api_data = response.json()
            
            # Process the API response
            processed_data = self.process_api_data(api_data)
            
            # Cache the successfully fetched data
            self.cached_data = processed_data
            self.failed_attempts = 0  # Reset failed attempts counter
            
            # Schedule UI updates to run on the main thread
            self.root.after(0, lambda: self._update_ui_with_data(processed_data))
            
        except Exception as e:
            # Increment failed attempts
            self.failed_attempts += 1
            
            # Use cached data if available
            if self.cached_data and self.failed_attempts <= self.max_retry_attempts:
                # Schedule UI update with cached data
                self.root.after(0, lambda: self._update_ui_with_cached_data(str(e)))
            else:
                # Handle errors on the main thread if no cache or too many failures
                self.root.after(0, lambda: self._handle_fetch_error(str(e)))
        finally:
            # Reset fetching flag
            self.is_fetching = False
    
    def _update_ui_with_cached_data(self, error_message):
        """Update UI with cached data when live fetch fails"""
        if not self.cached_data:
            self._handle_fetch_error(error_message)
            return
            
        # Update UI with cached data
        self.match_data = self.cached_data
        self.update_info_panel()
        self.populate_team_dropdown()
        self.update_dashboard()
        
        # Update status to show using cached data
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_updated_var.set(f"Last updated: Using cached data")
        self.status_var.set(f"Status: Network error ({self.failed_attempts}/{self.max_retry_attempts})")
        
        # Stop loading animation with warning
        self.stop_loading_animation(success=None)  # None means warning (yellow)
        
        # Show toast notification about using cached data
        self.show_toast_notification(f"Network error: {error_message}\nUsing cached data.")
    
    def _update_ui_with_data(self, processed_data):
        """Update UI with fetched data (runs on main thread)"""
        self.match_data = processed_data
        
        # Update UI
        self.update_info_panel()
        self.populate_team_dropdown()
        self.update_dashboard()
        
        # Update status and last updated time
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_updated_var.set(f"Last updated: {current_time}")
        self.status_var.set("Status: Data loaded")
        
        # Stop loading animation with success
        self.stop_loading_animation(success=True)
        
        # Flash the last updated time to draw attention
        self._flash_last_updated()
    
    def _handle_fetch_error(self, error_message):
        """Handle fetch errors (runs on main thread)"""
        self.status_var.set("Status: Error fetching data")
        messagebox.showerror("Error", f"Failed to fetch match data: {error_message}")
        
        # Stop loading animation with error
        self.stop_loading_animation(success=False)
    
    def _flash_last_updated(self, count=0):
        """Flash the last updated label to draw attention"""
        if count >= 6:  # Flash 3 times (on/off cycles)
            return
            
        # Toggle background color
        if count % 2 == 0:
            color = "#2ecc71"  # Green
        else:
            color = "#3498db"  # Default header color
            
        # Get the last updated label and change its background
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_y() == 0:  # Header frame
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):  # Controls frame
                        for control in child.winfo_children():
                            if isinstance(control, tk.Label) and "updated" in control.cget("text"):
                                control.config(bg=color)
                                break
        
        # Schedule next flash
        self.root.after(300, lambda: self._flash_last_updated(count + 1))
    
    def start_auto_refresh(self):
        """Start auto-refresh timer"""
        if self.auto_refresh.get():
            # Schedule the next refresh
            self.root.after(self.auto_refresh_interval * 1000, self.auto_refresh_callback)
    
    def auto_refresh_callback(self):
        """Auto refresh callback function"""
        if self.auto_refresh.get():
            # Fetch new data if auto-refresh is still enabled
            if not self.is_fetching:
                # Adjust refresh interval based on failures
                if self.failed_attempts > 0:
                    # Double the interval temporarily (up to 5 minutes max)
                    backoff_interval = min(self.auto_refresh_interval * (2 ** self.failed_attempts), 300)
                    self.root.after(backoff_interval * 1000, self.auto_refresh_callback)
                    return
                
                self.fetch_data()
            
            # Schedule the next refresh
            self.root.after(self.auto_refresh_interval * 1000, self.auto_refresh_callback)
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh.get():
            # Start auto-refresh if it was turned on
            self.start_auto_refresh()
            self.status_var.set(f"Status: Auto-refresh enabled ({self.auto_refresh_interval}s)")
        else:
            self.status_var.set("Status: Auto-refresh disabled")
    
    def process_api_data(self, api_data):
        """Process the API data to match our expected format"""
        processed_data = {
                "matchHeader": {
                "matchId": api_data.get("matchId", 0),
                "matchDescription": api_data.get("matchDesc", ""),
                "matchFormat": api_data.get("matchType", ""),
                "matchType": api_data.get("matchType", ""),
                    "complete": True,
                    "domestic": False,
                "teams": [],
                "seriesName": api_data.get("seriesName", ""),
                "seriesId": api_data.get("seriesId", 0),
                "status": api_data.get("status", ""),
                    "venue": {
                    "id": 0,
                    "name": api_data.get("venueInfo", {}).get("ground", ""),
                    "location": api_data.get("venueInfo", {}).get("city", ""),
                    "country": api_data.get("venueInfo", {}).get("country", ""),
                },
                "matchDate": api_data.get("matchHeader", {}).get("matchDate", ""),
                    "tossResults": {
                    "tossWinnerId": 0,
                    "tossWinnerName": api_data.get("tossInfo", "").split(" elected to ")[0] if "elected to" in api_data.get("tossInfo", "") else "",
                    "decision": api_data.get("tossInfo", "").split(" elected to ")[1] if "elected to" in api_data.get("tossInfo", "") else "",
                },
            },
            "scoreCard": []
        }
        
        # Extract teams
        if "scoreCard" in api_data and len(api_data["scoreCard"]) > 0:
            teams = []
            for inning in api_data.get("scoreCard", []):
                bat_team = {
                    "id": inning.get("batTeamDetails", {}).get("batTeamId", 0),
                    "name": inning.get("batTeamDetails", {}).get("batTeamName", ""),
                    "sName": inning.get("batTeamDetails", {}).get("batTeamShortName", ""),
                    "imgUrl": "",
                }
                bowl_team = {
                    "id": inning.get("bowlTeamDetails", {}).get("bowlTeamId", 0),
                    "name": inning.get("bowlTeamDetails", {}).get("bowlTeamName", ""),
                    "sName": inning.get("bowlTeamDetails", {}).get("bowlTeamShortName", ""),
                    "imgUrl": "",
                }
                
                # Add teams if not already added
                if bat_team["id"] not in [t.get("id") for t in teams]:
                    teams.append(bat_team)
                if bowl_team["id"] not in [t.get("id") for t in teams]:
                    teams.append(bowl_team)
            
            processed_data["matchHeader"]["teams"] = teams
        
        # Process innings
        for inning in api_data.get("scoreCard", []):
            bat_team_details = inning.get("batTeamDetails", {})
            bowl_team_details = inning.get("bowlTeamDetails", {})
            
            # Process batsmen
            batsmen = []
            for key, batsman in bat_team_details.get("batsmenData", {}).items():
                batsmen.append({
                    "name": batsman.get("batName", ""),
                    "runs": batsman.get("runs", 0),
                    "balls": batsman.get("balls", 0),
                    "fours": batsman.get("fours", 0),
                    "sixes": batsman.get("sixes", 0)
                })
            
            # Process bowlers
            bowlers = []
            for key, bowler in bowl_team_details.get("bowlersData", {}).items():
                overs = bowler.get("overs", 0)
                # Convert overs format (e.g. 4.2 means 4 overs and 2 balls)
                overs_decimal = float(overs) if isinstance(overs, (int, float)) else float(overs.replace("*", "")) if isinstance(overs, str) else 0
                
                bowlers.append({
                    "name": bowler.get("bowlName", ""),
                    "overs": overs_decimal,
                    "maidens": bowler.get("maidens", 0),
                    "runs": bowler.get("runs", 0),
                    "wickets": bowler.get("wickets", 0)
                })
            
            # Add innings to scorecard
            inning_data = {
                "inningsId": inning.get("inningsId", 0),
                "teamId": bat_team_details.get("batTeamId", 0),
                "team": bat_team_details.get("batTeamName", ""),
                "overs": inning.get("scoreDetails", {}).get("overs", 0),
                "runs": inning.get("scoreDetails", {}).get("runs", 0),
                "wickets": inning.get("scoreDetails", {}).get("wickets", 0),
                "batsmen": batsmen,
                "bowlers": bowlers
            }
            
            processed_data["scoreCard"].append(inning_data)
        
        # Add match progress data
        processed_data["matchProgress"] = {
            "overByOver": []
        }
        
        # If there are two innings, create over-by-over progress
        if len(processed_data["scoreCard"]) >= 2:
            team1_score = processed_data["scoreCard"][0]["runs"]
            team2_score = processed_data["scoreCard"][1]["runs"]
            max_overs = max(processed_data["scoreCard"][0].get("overs", 0), 
                          processed_data["scoreCard"][1].get("overs", 0))
            
            # Create simulated over-by-over progress
            # In a real app, you would extract this from the commentary or detailed data
            overs_list = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
            for over in overs_list:
                if over <= max_overs:
                    ratio = min(over / max_overs, 1.0)
                    processed_data["matchProgress"]["overByOver"].append({
                        "over": over,
                        "team1Score": int(team1_score * ratio),
                        "team2Score": int(team2_score * ratio) if over <= processed_data["scoreCard"][1].get("overs", 0) else None
                    })
        
        return processed_data
    
    def update_info_panel(self):
        """Update the info panel with match details"""
        if self.match_data:
            header = self.match_data["matchHeader"]
            
            # Set match title with all relevant information in a single line
            series = header["seriesName"]
            match_desc = header["matchDescription"]
            team1 = header["teams"][0]["name"]
            team2 = header["teams"][1]["name"]
            self.match_title_var.set(f"{series}: {team1} vs {team2} ({match_desc})")
            
            # Set status with more details
            self.status_display_var.set(f"Status: {header['status']}")
            
            # We've removed venue, date and toss information as requested
    
    def populate_team_dropdown(self):
        """Populate the team dropdown with teams from the match"""
        if self.match_data:
            teams = [team["name"] for team in self.match_data["matchHeader"]["teams"]]
            teams.append("Both Teams")  # Add option to view both teams
            
            self.teams = teams
            self.team_dropdown["values"] = teams
            
            # Select first team by default
            if teams:
                self.selected_team.set(teams[0])
    
    def update_dashboard(self, event=None):
        """Update the dashboard based on selected team and view"""
        selected_team = self.selected_team.get()
        selected_view = self.selected_view.get()
        
        # Clear previous content
        for widget in self.overview_tab.winfo_children():
            widget.destroy()
        for widget in self.batting_tab.winfo_children():
            widget.destroy()
        for widget in self.bowling_tab.winfo_children():
            widget.destroy()
        for widget in self.players_tab.winfo_children():
            widget.destroy()
        for widget in self.progress_tab.winfo_children():
            widget.destroy()
        
        # Create content for all tabs to ensure data is loaded
        self.create_overview_tab()
        self.create_batting_tab()
        self.create_bowling_tab()
        self.create_players_tab()
        self.create_progress_tab()
        
        # Select the correct tab based on the view
        if selected_view == "Overview":
            self.notebook.select(self.overview_tab)
        elif selected_view == "Batting Analysis":
            self.notebook.select(self.batting_tab)
        elif selected_view == "Bowling Analysis":
            self.notebook.select(self.bowling_tab)
        elif selected_view == "Player Stats":
            self.notebook.select(self.players_tab)
        elif selected_view == "Match Progress":
            self.notebook.select(self.progress_tab)
    
    def create_overview_tab(self):
        """Create content for the overview tab"""
        # Create a single frame for all graphs
        graphs_frame = ttk.LabelFrame(self.overview_tab, text="Match Statistics", padding=15)
        graphs_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create a figure with 2x2 subplots for equal sizing
        fig = plt.figure(figsize=(10, 8))
        
        # First graph: Team Comparison (top-left)
        ax1 = fig.add_subplot(2, 2, 1)
        teams = [inning["team"] for inning in self.match_data["scoreCard"]]
        scores = [inning["runs"] for inning in self.match_data["scoreCard"]]
        
        ax1.bar(teams, scores, color=['#3498db', '#e74c3c'], alpha=0.7)
        ax1.set_ylabel('Runs')
        ax1.set_title('Team Scores')
        
        # Second graph: Wickets comparison (top-right)
        ax2 = fig.add_subplot(2, 2, 2)
        wickets = [inning["wickets"] for inning in self.match_data["scoreCard"]]
        
        ax2.bar(teams, wickets, color=['#9b59b6', '#f39c12'], alpha=0.7)
        ax2.set_ylabel('Wickets')
        ax2.set_title('Team Wickets')
        
        # Third graph: Run distribution pie chart (bottom-left)
        ax3 = fig.add_subplot(2, 2, 3)
        
        # Get run distribution for both teams combined
        boundaries = 0
        singles_doubles = 0
        extras = 0
        
        for inning in self.match_data["scoreCard"]:
            for batsman in inning["batsmen"]:
                # Count boundaries (4s and 6s)
                boundaries += (batsman["fours"] * 4) + (batsman["sixes"] * 6)
                # Estimate singles and doubles (total runs - boundaries)
                singles_doubles += batsman["runs"] - ((batsman["fours"] * 4) + (batsman["sixes"] * 6))
            
            # Estimate extras as 5% of total runs for demo purposes
            extras += round(inning["runs"] * 0.05)
        
        labels = ['Boundaries', 'Singles & Doubles', 'Extras']
        sizes = [boundaries, singles_doubles, extras]
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        explode = (0.1, 0, 0)
        
        ax3.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
        ax3.axis('equal')
        ax3.set_title('Run Distribution')
        
        # Fourth graph: Run rate comparison (bottom-right)
        ax4 = fig.add_subplot(2, 2, 4)
        overs = [float(inning["overs"]) for inning in self.match_data["scoreCard"]]
        run_rates = [round(inning["runs"] / float(inning["overs"]), 2) for inning in self.match_data["scoreCard"]]
        
        ax4.bar(teams, run_rates, color=['#1abc9c', '#d35400'], alpha=0.7)
        ax4.set_ylabel('Run Rate')
        ax4.set_title('Team Run Rates')
        
        # Add values on top of bars
        for i, v in enumerate(run_rates):
            ax4.text(i, v + 0.1, str(v), ha='center')
        
        # Adjust layout
        plt.tight_layout()
        
        # Create canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, graphs_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Match summary text area
        summary_frame = ttk.LabelFrame(self.overview_tab, text="Match Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        summary_text = scrolledtext.ScrolledText(summary_frame, height=5, wrap=tk.WORD)
        summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Create a summary from the match data
        header = self.match_data["matchHeader"]
        innings1 = self.match_data["scoreCard"][0]
        innings2 = self.match_data["scoreCard"][1]
        
        summary = f"""
{header["teams"][0]["name"]} vs {header["teams"][1]["name"]} - {header["matchDescription"]}
Venue: {header["venue"]["name"]}, {header["venue"].get("location", "")}
Date: {header["matchDate"]}

{innings1["team"]} scored {innings1["runs"]}/{innings1["wickets"]} in {innings1["overs"]} overs.
Top scorer: {innings1["batsmen"][0]["name"]} ({innings1["batsmen"][0]["runs"]} runs off {innings1["batsmen"][0]["balls"]} balls)
Best bowler: {innings2["bowlers"][0]["name"]} ({innings2["bowlers"][0]["wickets"]}/{innings2["bowlers"][0]["runs"]})

{innings2["team"]} scored {innings2["runs"]}/{innings2["wickets"]} in {innings2["overs"]} overs.
Top scorer: {innings2["batsmen"][0]["name"]} ({innings2["batsmen"][0]["runs"]} runs off {innings2["batsmen"][0]["balls"]} balls)
Best bowler: {innings1["bowlers"][0]["name"]} ({innings1["bowlers"][0]["wickets"]}/{innings1["bowlers"][0]["runs"]})

Result: {header["status"]}
        """
        
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)
    
    def create_batting_tab(self):
        """Create content for the batting analysis tab"""
        # Top frame with controls
        control_frame = tk.Frame(self.batting_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter by innings
        innings_label = tk.Label(control_frame, text="Select Innings:")
        innings_label.pack(side=tk.LEFT, padx=(0, 10))
        
        innings_var = tk.StringVar(value="Innings 1")
        innings_dropdown = ttk.Combobox(
            control_frame,
            textvariable=innings_var,
            values=["Innings 1", "Innings 2"],
            state="readonly",
            width=15
        )
        innings_dropdown.pack(side=tk.LEFT, padx=(0, 20))
        
        # Analysis type
        analysis_label = tk.Label(control_frame, text="Analysis Type:")
        analysis_label.pack(side=tk.LEFT, padx=(0, 5))
        
        analysis_var = tk.StringVar(value="Runs Distribution")
        analysis_dropdown = ttk.Combobox(
            control_frame,
            textvariable=analysis_var,
            values=["Runs Distribution", "Balls Faced", "Strike Rate", "Boundary %"],
            state="readonly",
            width=15
        )
        analysis_dropdown.pack(side=tk.LEFT)
        
        # Create frame for graphs
        graphs_frame = tk.Frame(self.batting_tab)
        graphs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left graph: Runs scored by batsmen
        runs_frame = ttk.LabelFrame(graphs_frame, text="Runs by Batsmen")
        runs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        fig1, ax1 = plt.subplots(figsize=(4, 4))
                
        # Get data for the first innings - FIXING THE ERROR HERE
        innings = self.match_data["scoreCard"][0]
        batsmen = innings["batsmen"][:6]  # Show top 6 batsmen
        
        names = [batsman["name"] for batsman in batsmen]
        runs = [batsman["runs"] for batsman in batsmen]
        
        # Create horizontal bar chart
        bars = ax1.barh(names, runs, color='#3498db', alpha=0.7)
        ax1.set_xlabel('Runs')
        ax1.set_title('Top Batsmen Performance')
        
        # Add values at the end of bars
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width}', 
                     ha='left', va='center')
        plt.tight_layout()
        fig1.subplots_adjust(left=0.25)
        canvas1 = FigureCanvasTkAgg(fig1, runs_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right graph: Strike rates
        strike_frame = ttk.LabelFrame(graphs_frame, text="Batsmen Strike Rates")
        strike_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        
        # Calculate strike rates
        strike_rates = [round((batsman["runs"] / batsman["balls"]) * 100, 1) for batsman in batsmen]
        
        # Create horizontal bar chart with different color
        bars = ax2.barh(names, strike_rates, color='#e74c3c', alpha=0.7)
        ax2.set_xlabel('Strike Rate')
        ax2.set_title('Batsmen Strike Rates')
        
        # Add values at the end of bars
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width}', 
                     ha='left', va='center')
        plt.tight_layout()
        fig1.subplots_adjust(left=0.25)
        canvas2 = FigureCanvasTkAgg(fig2, strike_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bottom frame for batting scorecard
        scorecard_frame = ttk.LabelFrame(self.batting_tab, text="Batting Scorecard", padding=5)
        scorecard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for batting scorecard
        cols = ('Batsman', 'Runs', 'Balls', '4s', '6s', 'SR')
        batting_table = ttk.Treeview(scorecard_frame, columns=cols, show='headings', height=10)
        
        # Configure column headings
        for col in cols:
            batting_table.heading(col, text=col)
            if col == 'Batsman':
                batting_table.column(col, width=150, anchor='w')
            else:
                batting_table.column(col, width=80, anchor='center')
        
        # Insert data
        for batsman in innings["batsmen"]:
            strike_rate = round((batsman["runs"] / batsman["balls"]) * 100, 1) if batsman["balls"] > 0 else 0
            batting_table.insert('', 'end', values=(
                batsman["name"],
                batsman["runs"],
                batsman["balls"],
                batsman["fours"],
                batsman["sixes"],
                strike_rate
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(scorecard_frame, orient=tk.VERTICAL, command=batting_table.yview)
        batting_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        batting_table.pack(fill=tk.BOTH, expand=True)
        
        # Update function for changing innings or analysis type
        def update_batting_analysis(*args):
            innings_idx = 0 if innings_var.get() == "Innings 1" else 1
            analysis_type = analysis_var.get()
            
            # Clear previous graphs
            for widget in runs_frame.winfo_children():
                widget.destroy()
            for widget in strike_frame.winfo_children():
                widget.destroy()
            
            # Update data
            innings = self.match_data["scoreCard"][innings_idx]
            batsmen = innings["batsmen"][:6]  # Show top 6 batsmen
            names = [batsman["name"] for batsman in batsmen]
            
            # Update batting table
            batting_table.delete(*batting_table.get_children())
            for batsman in innings["batsmen"]:
                strike_rate = round((batsman["runs"] / batsman["balls"]) * 100, 1) if batsman["balls"] > 0 else 0
                batting_table.insert('', 'end', values=(
                    batsman["name"],
                    batsman["runs"],
                    batsman["balls"],
                    batsman["fours"],
                    batsman["sixes"],
                    strike_rate
                ))
            
            # Update first graph based on analysis type
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            
            if analysis_type == "Runs Distribution":
                # Sort data by runs (descending)
                sorted_indices = sorted(range(len(names)), key=lambda i: runs[i], reverse=True)
                sorted_names = [names[i] for i in sorted_indices]
                sorted_runs = [runs[i] for i in sorted_indices]
                
                # Create horizontal bar chart
                bars = ax1.barh(sorted_names, sorted_runs, color='#3498db', alpha=0.7)
                ax1.set_xlabel('Runs')
                ax1.set_title('Runs by Batsmen')
                
                # Add values at the end of bars
                for bar in bars:
                    width = bar.get_width()
                    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                            ha='left', va='center')
                
                # Ensure y-labels are fully visible
                plt.tight_layout()
                fig1.subplots_adjust(left=0.25)  # Add more padding on left for names
            
            elif analysis_type == "Balls Faced":
                # Sort data by balls faced (descending)
                sorted_indices = sorted(range(len(names)), key=lambda i: balls[i], reverse=True)
                sorted_names = [names[i] for i in sorted_indices]
                sorted_balls = [balls[i] for i in sorted_indices]
                
                # Create horizontal bar chart
                bars = ax1.barh(sorted_names, sorted_balls, color='#9b59b6', alpha=0.7)
                ax1.set_xlabel('Balls Faced')
                ax1.set_title('Balls Faced by Batsmen')
                
                # Add values at the end of bars
                for bar in bars:
                    width = bar.get_width()
                    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                            ha='left', va='center')
                            
                # Ensure y-labels are fully visible
                plt.tight_layout()
                fig1.subplots_adjust(left=0.25)  # Add more padding on left for names
            
            elif analysis_type == "Strike Rate":
                # Sort data by strike rate (descending)
                strike_rates = [round((batsman["runs"] / batsman["balls"]) * 100, 1) for batsman in batsmen]
                sorted_indices = sorted(range(len(names)), key=lambda i: strike_rates[i], reverse=True)
                sorted_names = [names[i] for i in sorted_indices]
                sorted_strike_rates = [strike_rates[i] for i in sorted_indices]
                
                # Create horizontal bar chart
                bars = ax1.barh(sorted_names, sorted_strike_rates, color='#e74c3c', alpha=0.7)
                ax1.set_xlabel('Strike Rate')
                ax1.set_title('Batsmen Strike Rates')
                
                # Add values at the end of bars
                for bar in bars:
                    width = bar.get_width()
                    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width}', 
                            ha='left', va='center')
                
                # Ensure y-labels are fully visible
                plt.tight_layout()
                fig1.subplots_adjust(left=0.25)  # Add more padding on left for names
                
            elif analysis_type == "Boundary %":
                # Calculate and sort by boundary percentage
                boundary_pcts = [round(((batsman["fours"] * 4 + batsman["sixes"] * 6) / batsman["runs"]) * 100, 1) 
                                if batsman["runs"] > 0 else 0 for batsman in batsmen]
                sorted_indices = sorted(range(len(names)), key=lambda i: boundary_pcts[i], reverse=True)
                sorted_names = [names[i] for i in sorted_indices]
                sorted_boundary_pcts = [boundary_pcts[i] for i in sorted_indices]
                
                # Create horizontal bar chart
                bars = ax1.barh(sorted_names, sorted_boundary_pcts, color='#9b59b6', alpha=0.7)
                ax1.set_xlabel('Boundary %')
                ax1.set_title('Percentage of Runs from Boundaries')
                
                # Add values at the end of bars
                for bar in bars:
                    width = bar.get_width()
                    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width}', 
                            ha='left', va='center')
                
                # Ensure y-labels are fully visible
                plt.tight_layout()
                fig1.subplots_adjust(left=0.25)  # Add more padding on left for names
            
            canvas1 = FigureCanvasTkAgg(fig1, runs_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Update second graph
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            
            # Pie chart showing runs from boundaries vs non-boundaries
            total_runs = sum(batsman["runs"] for batsman in innings["batsmen"])
            boundary_runs = sum((batsman["fours"] * 4) + (batsman["sixes"] * 6) for batsman in innings["batsmen"])
            non_boundary_runs = total_runs - boundary_runs
            
            labels = ['Boundary Runs', 'Non-Boundary Runs']
            sizes = [boundary_runs, non_boundary_runs]
            colors = ['#e74c3c', '#3498db']
            explode = (0.1, 0)
            
            ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
            ax2.axis('equal')
            ax2.set_title('Run Distribution')
            
            canvas2 = FigureCanvasTkAgg(fig2, strike_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind dropdowns to update function
        innings_var.trace('w', update_batting_analysis)
        analysis_var.trace('w', update_batting_analysis)
    
    def create_bowling_tab(self):
        """Create content for the bowling analysis tab"""
        # Top frame with controls
        control_frame = tk.Frame(self.bowling_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter by innings
        innings_label = tk.Label(control_frame, text="Select Innings:")
        innings_label.pack(side=tk.LEFT, padx=(0, 10))
        
        innings_var = tk.StringVar(value="Innings 1")
        innings_dropdown = ttk.Combobox(
            control_frame,
            textvariable=innings_var,
            values=["Innings 1", "Innings 2"],
            state="readonly",
            width=15
        )
        innings_dropdown.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create frame for graphs
        graphs_frame = tk.Frame(self.bowling_tab)
        graphs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left graph: Wickets taken by bowlers
        wickets_frame = ttk.LabelFrame(graphs_frame, text="Wickets by Bowlers")
        wickets_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        
        # Get data for the second innings (bowling figures for first team)
        innings = self.match_data["scoreCard"][1]  # Second innings
        bowlers = innings["bowlers"]
        
        names = [bowler["name"] for bowler in bowlers]
        wickets = [bowler["wickets"] for bowler in bowlers]
        
        # Sort data by wickets (descending)
        sorted_indices = sorted(range(len(names)), key=lambda i: wickets[i], reverse=True)
        sorted_names = [names[i] for i in sorted_indices]
        sorted_wickets = [wickets[i] for i in sorted_indices]
        
        # Create horizontal bar chart
        bars = ax1.barh(sorted_names, sorted_wickets, color='#3498db', alpha=0.7)
        ax1.set_xlabel('Wickets')
        ax1.set_title('Wickets by Bowlers')
        
        # Add values at the end of bars
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width}', 
                    ha='left', va='center')
        
        # Ensure y-labels are fully visible
        plt.tight_layout()
        fig1.subplots_adjust(left=0.25)  # Add more padding on left for names
        
        canvas1 = FigureCanvasTkAgg(fig1, wickets_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right graph: Economy rates
        economy_frame = ttk.LabelFrame(graphs_frame, text="Economy Rates")
        economy_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        
        # Calculate economy rates
        economy = [round(bowler["runs"] / float(bowler["overs"]), 2) for bowler in bowlers]
        
        # Sort data by economy (ascending - lower is better)
        sorted_indices = sorted(range(len(names)), key=lambda i: economy[i])
        sorted_names = [names[i] for i in sorted_indices]
        sorted_economy = [economy[i] for i in sorted_indices]
        
        # Create horizontal bar chart
        bars = ax2.barh(sorted_names, sorted_economy, color='#e74c3c', alpha=0.7)
        ax2.set_xlabel('Economy Rate')
        ax2.set_title('Economy Rates')
        
        # Add values at the end of bars
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width}', 
                    ha='left', va='center')
        
        # Ensure y-labels are fully visible
        plt.tight_layout()
        fig2.subplots_adjust(left=0.25)  # Add more padding on left for names
        
        canvas2 = FigureCanvasTkAgg(fig2, economy_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bottom frame for bowling scorecard
        scorecard_frame = ttk.LabelFrame(self.bowling_tab, text="Bowling Scorecard", padding=10)
        scorecard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for bowling scorecard
        cols = ('Bowler', 'Overs', 'Maidens', 'Runs', 'Wickets', 'Economy')
        bowling_table = ttk.Treeview(scorecard_frame, columns=cols, show='headings', height=10)
        
        # Configure column headings
        for col in cols:
            bowling_table.heading(col, text=col)
            if col == 'Bowler':
                bowling_table.column(col, width=150, anchor='w')
            else:
                bowling_table.column(col, width=80, anchor='center')
        
        # Insert data
        for bowler in innings["bowlers"]:
            economy = round(bowler["runs"] / float(bowler["overs"]), 2)
            bowling_table.insert('', 'end', values=(
                bowler["name"],
                bowler["overs"],
                bowler["maidens"],
                bowler["runs"],
                bowler["wickets"],
                economy
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(scorecard_frame, orient=tk.VERTICAL, command=bowling_table.yview)
        bowling_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        bowling_table.pack(fill=tk.BOTH, expand=True)
        
        # Update function for changing innings
        def update_bowling_analysis(*args):
            innings_idx = 0 if innings_var.get() == "Innings 2" else 1  # Reverse logic for bowling
            
            # Clear previous graphs
            for widget in wickets_frame.winfo_children():
                widget.destroy()
            for widget in economy_frame.winfo_children():
                widget.destroy()
            
            # Update data
            innings = self.match_data["scoreCard"][innings_idx]
            bowlers = innings["bowlers"]
            names = [bowler["name"] for bowler in bowlers]
            
            # Update bowling table
            bowling_table.delete(*bowling_table.get_children())
            for bowler in innings["bowlers"]:
                economy = round(bowler["runs"] / float(bowler["overs"]), 2)
                bowling_table.insert('', 'end', values=(
                    bowler["name"],
                    bowler["overs"],
                    bowler["maidens"],
                    bowler["runs"],
                    bowler["wickets"],
                    economy
                ))
            
            # Update wickets graph
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            wickets = [bowler["wickets"] for bowler in bowlers]
            
            bars = ax1.barh(names, wickets, color='#3498db', alpha=0.7)
            ax1.set_xlabel('Wickets')
            ax1.set_title('Wickets by Bowlers')
            
            # Add values at the end of bars
            for bar in bars:
                width = bar.get_width()
                ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width}', 
                         ha='left', va='center')
            
            canvas1 = FigureCanvasTkAgg(fig1, wickets_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Update economy graph
            fig2, ax2 = plt.subplots(figsize=(4, 4))
            economy_rates = [round(bowler["runs"] / float(bowler["overs"]), 2) for bowler in bowlers]
            
            bars = ax2.barh(names, economy_rates, color='#e74c3c', alpha=0.7)
            ax2.set_xlabel('Economy Rate')
            ax2.set_title('Bowler Economy Rates')
            
            # Add values at the end of bars
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width}', 
                         ha='left', va='center')
            
            canvas2 = FigureCanvasTkAgg(fig2, economy_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind dropdown to update function
        innings_var.trace('w', update_bowling_analysis)
    
    def create_players_tab(self):
        """Create content for player stats tab"""
        # Create frame for team selection
        team_frame = tk.Frame(self.players_tab)
        team_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Team selection
        team_label = tk.Label(team_frame, text="Select Team:")
        team_label.pack(side=tk.LEFT, padx=(0, 10))
        
        team_var = tk.StringVar(value=self.match_data["matchHeader"]["teams"][0]["name"])
        team_dropdown = ttk.Combobox(
            team_frame,
            textvariable=team_var,
            values=[team["name"] for team in self.match_data["matchHeader"]["teams"]],
            state="readonly",
            width=15
        )
        team_dropdown.pack(side=tk.LEFT)
        
        # Create player list frame
        players_frame = tk.Frame(self.players_tab)
        players_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Player list
        player_list_frame = ttk.LabelFrame(players_frame, text="Players", padding=10)
        player_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create listbox for players
        players_listbox = tk.Listbox(player_list_frame, height=15, selectmode=tk.SINGLE)
        players_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(player_list_frame, orient=tk.VERTICAL, command=players_listbox.yview)
        players_listbox.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right side: Player details
        player_details_frame = ttk.LabelFrame(players_frame, text="Player Details", padding=10)
        player_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Player image (placeholder)
        # img_frame = tk.Frame(player_details_frame, height=150, width=150)
        # img_frame.pack(pady=10)
        # img_frame.pack_propagate(False)
        
        # # Create a circle placeholder for player image
        # canvas = tk.Canvas(img_frame, width=150, height=150, bg="#f0f0f0", highlightthickness=0)
        # canvas.pack()
        # canvas.create_oval(10, 10, 140, 140, fill="#3498db", outline="#2980b9", width=2)
        # canvas.create_text(75, 75, text="Player\nPhoto", fill="white", font=("Arial", 12, "bold"))
        
        # Player info
        info_frame = tk.Frame(player_details_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Player name
        name_var = tk.StringVar(value="Player Name")
        name_label = tk.Label(info_frame, textvariable=name_var, font=("Arial", 14, "bold"))
        name_label.pack(anchor="w", pady=5)
        
        # Role
        role_var = tk.StringVar(value="Role: Batsman")
        role_label = tk.Label(info_frame, textvariable=role_var)
        role_label.pack(anchor="w", pady=2)
        
        # Create stats frame with two columns
        stats_frame = tk.Frame(info_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left column
        left_stats = tk.Frame(stats_frame)
        left_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right column
        right_stats = tk.Frame(stats_frame)
        right_stats.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Batting stats
        batting_header = tk.Label(left_stats, text="Batting", font=("Arial", 11, "bold"))
        batting_header.pack(anchor="w", pady=(0, 5))
        
        runs_var = tk.StringVar(value="Runs: 0")
        runs_label = tk.Label(left_stats, textvariable=runs_var)
        runs_label.pack(anchor="w", pady=1)
        
        balls_var = tk.StringVar(value="Balls: 0")
        balls_label = tk.Label(left_stats, textvariable=balls_var)
        balls_label.pack(anchor="w", pady=1)
        
        sr_var = tk.StringVar(value="Strike Rate: 0.0")
        sr_label = tk.Label(left_stats, textvariable=sr_var)
        sr_label.pack(anchor="w", pady=1)
        
        boundaries_var = tk.StringVar(value="4s: 0, 6s: 0")
        boundaries_label = tk.Label(left_stats, textvariable=boundaries_var)
        boundaries_label.pack(anchor="w", pady=1)
        
        # Bowling stats
        bowling_header = tk.Label(right_stats, text="Bowling", font=("Arial", 11, "bold"))
        bowling_header.pack(anchor="w", pady=(0, 5))
        
        overs_var = tk.StringVar(value="Overs: 0")
        overs_label = tk.Label(right_stats, textvariable=overs_var)
        overs_label.pack(anchor="w", pady=1)
        
        wickets_var = tk.StringVar(value="Wickets: 0")
        wickets_label = tk.Label(right_stats, textvariable=wickets_var)
        wickets_label.pack(anchor="w", pady=1)
        
        eco_var = tk.StringVar(value="Economy: 0.0")
        eco_label = tk.Label(right_stats, textvariable=eco_var)
        eco_label.pack(anchor="w", pady=1)
        
        maidens_var = tk.StringVar(value="Maidens: 0")
        maidens_label = tk.Label(right_stats, textvariable=maidens_var)
        maidens_label.pack(anchor="w", pady=1)
        
        # Performance graph
        graph_frame = ttk.LabelFrame(player_details_frame, text="Performance", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Helper function to populate player details
        def show_player_details(event):
            selection = players_listbox.curselection()
            if not selection:
                return
                
            idx = selection[0]
            player_name = players_listbox.get(idx)
            
            # Find player in match data
            selected_team = team_var.get()
            team_idx = 0 if selected_team == self.match_data["matchHeader"]["teams"][0]["name"] else 1
            innings_idx = team_idx  # For batting
            bowling_idx = 1 - team_idx  # For bowling (opposite team's innings)
            
            # Find batting stats
            batting_data = None
            for batsman in self.match_data["scoreCard"][innings_idx]["batsmen"]:
                if batsman["name"] == player_name:
                    batting_data = batsman
                    break
            
            # Find bowling stats
            bowling_data = None
            for bowler in self.match_data["scoreCard"][bowling_idx]["bowlers"]:
                if bowler["name"] == player_name:
                    bowling_data = bowler
                    break
            
            # Update player details
            name_var.set(player_name)
            
            # Determine role based on available data
            role = "All-rounder" if batting_data and bowling_data else "Batsman" if batting_data else "Bowler" if bowling_data else "Unknown"
            role_var.set(f"Role: {role}")
            
            # Update batting stats
            if batting_data:
                runs_var.set(f"Runs: {batting_data['runs']}")
                balls_var.set(f"Balls: {batting_data['balls']}")
                sr = round((batting_data['runs'] / batting_data['balls']) * 100, 1) if batting_data['balls'] > 0 else 0
                sr_var.set(f"Strike Rate: {sr}")
                boundaries_var.set(f"4s: {batting_data['fours']}, 6s: {batting_data['sixes']}")
            else:
                runs_var.set("Runs: --")
                balls_var.set("Balls: --")
                sr_var.set("Strike Rate: --")
                boundaries_var.set("4s: --, 6s: --")
            
            # Update bowling stats
            if bowling_data:
                overs_var.set(f"Overs: {bowling_data['overs']}")
                wickets_var.set(f"Wickets: {bowling_data['wickets']}")
                eco = round(bowling_data['runs'] / float(bowling_data['overs']), 2)
                eco_var.set(f"Economy: {eco}")
                maidens_var.set(f"Maidens: {bowling_data['maidens']}")
            else:
                overs_var.set("Overs: --")
                wickets_var.set("Wickets: --")
                eco_var.set("Economy: --")
                maidens_var.set("Maidens: --")
            
            # Update performance graph
            for widget in graph_frame.winfo_children():
                widget.destroy()
            
            if batting_data:
                fig, ax = plt.subplots(figsize=(6, 3))
                
                # Simple bar chart showing runs composition
                categories = ['1s & 2s', '4s', '6s']
                values = [
                    batting_data["runs"] - (batting_data["fours"] * 4) - (batting_data["sixes"] * 6),
                    batting_data["fours"] * 4,
                    batting_data["sixes"] * 6
                ]
                
                colors = ['#3498db', '#2ecc71', '#e74c3c']
                ax.bar(categories, values, color=colors, alpha=0.7)
                ax.set_title('Runs Breakdown')
                
                for i, v in enumerate(values):
                    ax.text(i, v + 1, str(v), ha='center')
                
                canvas = FigureCanvasTkAgg(fig, graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        players_listbox.bind('<<ListboxSelect>>', show_player_details)
        
        # Function to update player list for selected team
        def update_player_list(*args):
            selected_team = team_var.get()
            players_listbox.delete(0, tk.END)
            
            # Find team index
            team_idx = 0 if selected_team == self.match_data["matchHeader"]["teams"][0]["name"] else 1
            innings_idx = team_idx
            
            # Get all players (combine batsmen and bowlers)
            players = set()
            
            # Add batsmen
            for batsman in self.match_data["scoreCard"][innings_idx]["batsmen"]:
                players.add(batsman["name"])
            
            # Add bowlers (from opposite team's innings)
            bowling_idx = 1 - team_idx  # Opposite team's innings
            for bowler in self.match_data["scoreCard"][bowling_idx]["bowlers"]:
                players.add(bowler["name"])
            
            # Add players to listbox
            for player in sorted(players):
                players_listbox.insert(tk.END, player)
        
        # Initial update
        update_player_list()
        
        # Bind team dropdown to update function
        team_var.trace('w', update_player_list)
    
    def create_progress_tab(self):
        """Create content for the match progress tab"""
        # Create frame for the graph
        graph_frame = ttk.LabelFrame(self.progress_tab, text="Match Progress", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a larger figure for better visibility
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Get progress data
        progress_data = self.match_data["matchProgress"]["overByOver"]
        overs = [entry["over"] for entry in progress_data]
        team1_scores = [entry["team1Score"] for entry in progress_data]
        team2_scores = [entry["team2Score"] for entry in progress_data]
        
        team1_name = self.match_data["scoreCard"][0]["team"]
        team2_name = self.match_data["scoreCard"][1]["team"]
        
        # Plot with improved styling
        ax.plot(overs, team1_scores, marker='o', markersize=6, linestyle='-', linewidth=3, 
                label=team1_name, color='#113955')  # Using the primary color
        ax.plot(overs, team2_scores, marker='s', markersize=6, linestyle='-', linewidth=3, 
                label=team2_name, color='#8c1c13')  # Using the secondary color
        
        # Add background shading
        ax.fill_between(overs, team1_scores, alpha=0.1, color='#113955')
        ax.fill_between(overs, team2_scores, alpha=0.1, color='#8c1c13')
        
        # Improve axis labels and title
        ax.set_xlabel('Overs', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Run Progress Throughout the Match', fontsize=14, fontweight='bold', pad=15)
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Improve legend
        ax.legend(fontsize=11, frameon=True, fancybox=True, framealpha=0.8, loc='upper left')
        
        # Annotate key points
        for i in range(len(overs)):
            # Annotate at regular intervals to avoid crowding
            if i % 3 == 0 or i == len(overs)-1:  
                ax.annotate(f"{team1_scores[i]}", (overs[i], team1_scores[i]),
                            textcoords="offset points", xytext=(0,10), ha='center',
                            fontweight='bold', fontsize=9)
                ax.annotate(f"{team2_scores[i]}", (overs[i], team2_scores[i]),
                            textcoords="offset points", xytext=(0,-15), ha='center',
                            fontweight='bold', fontsize=9)
        
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add analysis section
        analysis_frame = ttk.LabelFrame(self.progress_tab, text="Match Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create two columns for key stats
        left_stats = tk.Frame(analysis_frame)
        left_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_stats = tk.Frame(analysis_frame)
        right_stats.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Calculate key stats
        innings1 = self.match_data["scoreCard"][0]
        innings2 = self.match_data["scoreCard"][1]
        
        # Run rate progression
        rr_progression = []
        for i in range(len(progress_data)):
            over = progress_data[i]["over"]
            team1_rr = round(progress_data[i]["team1Score"] / over, 2) if over > 0 else 0
            team2_rr = round(progress_data[i]["team2Score"] / over, 2) if over > 0 else 0
            rr_progression.append((over, team1_rr, team2_rr))
        
        # Find powerplay scores (first 10 overs)
        powerplay_idx = next((i for i, entry in enumerate(progress_data) if entry["over"] >= 10), 0)
        powerplay1 = progress_data[powerplay_idx]["team1Score"] if powerplay_idx < len(progress_data) else 0
        powerplay2 = progress_data[powerplay_idx]["team2Score"] if powerplay_idx < len(progress_data) else 0
        
        # Find middle overs scores (11-40)
        middle_idx = next((i for i, entry in enumerate(progress_data) if entry["over"] >= 40), len(progress_data) - 1)
        middle1 = progress_data[middle_idx]["team1Score"] - powerplay1 if middle_idx < len(progress_data) else 0
        middle2 = progress_data[middle_idx]["team2Score"] - powerplay2 if middle_idx < len(progress_data) else 0
        
        # Death overs (41-50)
        death1 = innings1["runs"] - progress_data[middle_idx]["team1Score"] if middle_idx < len(progress_data) else 0
        death2 = innings2["runs"] - progress_data[middle_idx]["team2Score"] if middle_idx < len(progress_data) else 0
        
        # Left column stats
        tk.Label(left_stats, text=f"Powerplay Score (1-10 overs)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        tk.Label(left_stats, text=f"{team1_name}: {powerplay1} runs").pack(anchor="w")
        tk.Label(left_stats, text=f"{team2_name}: {powerplay2} runs").pack(anchor="w", pady=(0, 10))
        
        tk.Label(left_stats, text=f"Middle Overs (11-40)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        tk.Label(left_stats, text=f"{team1_name}: {middle1} runs").pack(anchor="w")
        tk.Label(left_stats, text=f"{team2_name}: {middle2} runs").pack(anchor="w", pady=(0, 10))
        
        tk.Label(left_stats, text=f"Death Overs (41-50)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        tk.Label(left_stats, text=f"{team1_name}: {death1} runs").pack(anchor="w")
        tk.Label(left_stats, text=f"{team2_name}: {death2} runs").pack(anchor="w")
        
        # Right column stats
        tk.Label(right_stats, text=f"Key Moments", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        
        # Find key moments (biggest run differences)
        run_diffs = [(i, team2_scores[i] - team1_scores[i]) for i in range(len(overs))]
        max_diff = max(run_diffs, key=lambda x: x[1])
        min_diff = min(run_diffs, key=lambda x: x[1])
        
        tk.Label(right_stats, text=f"Biggest lead for {team2_name}: {max_diff[1]} runs (over {overs[max_diff[0]]})").pack(anchor="w")
        tk.Label(right_stats, text=f"Biggest lead for {team1_name}: {-min_diff[1]} runs (over {overs[min_diff[0]]})").pack(anchor="w", pady=(0, 10))
        
        # Find over with highest scoring
        over_scores1 = [team1_scores[i] - team1_scores[i-1] if i > 0 else team1_scores[0] for i in range(len(team1_scores))]
        over_scores2 = [team2_scores[i] - team2_scores[i-1] if i > 0 else team2_scores[0] for i in range(len(team2_scores))]
        
        max_over1_idx = max(range(len(over_scores1)), key=lambda i: over_scores1[i])
        max_over2_idx = max(range(len(over_scores2)), key=lambda i: over_scores2[i])
        
        self.create_progress_stat_card(right_stats, "Highest Scoring Over", 
            f"{team1_name}: {over_scores1[max_over1_idx]} runs (over {overs[max_over1_idx]})\n{team2_name}: {over_scores2[max_over2_idx]} runs (over {overs[max_over2_idx]})")
    
    def create_progress_stat_card(self, parent, title, value):
        """Create a styled stat card for the progress tab"""
        card = tk.Frame(parent, bd=1, relief=tk.RAISED, padx=10, pady=10, bg='white')
        card.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(card, text=title, font=("Arial", 11, "bold"), bg='white', fg='#444')
        title_label.pack(anchor='w')
        
        ttk.Separator(card, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        value_label = tk.Label(card, text=value, font=("Arial", 10), bg='white', justify=tk.LEFT)
        value_label.pack(anchor='w')
        
        return card
    
    def export_data(self):
        """Export data to JSON file"""
        if not self.match_data:
            messagebox.showinfo("Export", "No data to export.")
            return
        
        try:
            from tkinter import filedialog
            import json
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Match Data"
            )
            
            if not file_path:
                return  # User cancelled
                
            # Save data to file
            with open(file_path, 'w') as f:
                json.dump(self.match_data, f, indent=2)
                
            # Show success message
            self.show_toast_notification(f"Data exported successfully to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def show_toast_notification(self, message):
        """Show a temporary toast notification"""
        # Create toast frame
        toast = tk.Frame(self.root, bg="#333333", padx=10, pady=10)
        
        # Create message label
        msg_label = tk.Label(
            toast, 
            text=message,
            bg="#333333",
            fg="white",
            font=("Arial", 10),
            justify=tk.LEFT,
            wraplength=300
        )
        msg_label.pack()
        
        # Position at bottom center
        self.root.update_idletasks()
        width = toast.winfo_reqwidth()
        root_width = self.root.winfo_width()
        x = (root_width - width) // 2
        toast.place(x=x, y=self.root.winfo_height() - 100)
        
        # Schedule removal
        self.root.after(5000, lambda: toast.destroy())
    
    def show_detailed_analysis(self):
        """Show detailed analysis in a new window"""
        if not self.match_data:
            messagebox.showerror("Error", "No match data available for analysis")
            return
        
        # Create a new window
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Detailed Match Analysis")
        analysis_window.geometry("800x600")
        
        # Create main frame with scrollbars
        main_frame = tk.Frame(analysis_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add canvas and scrollbars for scrolling
        canvas = tk.Canvas(main_frame)
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        # Configure scrollbars
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Create a frame inside the canvas to hold the content
        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Create a notebook with tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Head to head tab
        h2h_tab = ttk.Frame(notebook)
        notebook.add(h2h_tab, text="Head to Head")
        
        # Performance comparison tab
        perf_tab = ttk.Frame(notebook)
        notebook.add(perf_tab, text="Performance Metrics")
        
        # Generate basic head to head stats
        team1_name = self.match_data["scoreCard"][0]["team"]
        team2_name = self.match_data["scoreCard"][1]["team"]
        
        h2h_frame = ttk.LabelFrame(h2h_tab, text=f"{team1_name} vs {team2_name}", padding=10)
        h2h_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create comparison metrics
        metrics = [
            ("Total Runs", self.match_data["scoreCard"][0]["runs"], self.match_data["scoreCard"][1]["runs"]),
            ("Wickets Lost", self.match_data["scoreCard"][0]["wickets"], self.match_data["scoreCard"][1]["wickets"]),
            ("Overs Played", self.match_data["scoreCard"][0]["overs"], self.match_data["scoreCard"][1]["overs"]),
            ("Run Rate", round(self.match_data["scoreCard"][0]["runs"] / float(self.match_data["scoreCard"][0]["overs"]), 2),
                        round(self.match_data["scoreCard"][1]["runs"] / float(self.match_data["scoreCard"][1]["overs"]), 2)),
            ("Total Boundaries", sum(b["fours"] for b in self.match_data["scoreCard"][0]["batsmen"]) + 
                                 sum(b["sixes"] for b in self.match_data["scoreCard"][0]["batsmen"]),
                                 sum(b["fours"] for b in self.match_data["scoreCard"][1]["batsmen"]) + 
                                 sum(b["sixes"] for b in self.match_data["scoreCard"][1]["batsmen"])),
            ("Batting Strike Rate", 
                round(100 * self.match_data["scoreCard"][0]["runs"] / 
                      sum(b["balls"] for b in self.match_data["scoreCard"][0]["batsmen"]), 2),
                round(100 * self.match_data["scoreCard"][1]["runs"] / 
                      sum(b["balls"] for b in self.match_data["scoreCard"][1]["batsmen"]), 2)),
            ("Bowling Economy", 
                round(self.match_data["scoreCard"][1]["runs"] / 
                      sum(float(b["overs"]) for b in self.match_data["scoreCard"][1]["bowlers"]), 2),
                round(self.match_data["scoreCard"][0]["runs"] / 
                      sum(float(b["overs"]) for b in self.match_data["scoreCard"][0]["bowlers"]), 2))
        ]
        
        # Create comparison table
        for i, (metric, team1_val, team2_val) in enumerate(metrics):
            row_frame = tk.Frame(h2h_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            # Left team
            team1_frame = tk.Frame(row_frame, width=300)
            team1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(team1_frame, text=str(team1_val), font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
            
            # Center metric name
            metric_frame = tk.Frame(row_frame, width=200)
            metric_frame.pack(side=tk.LEFT)
            tk.Label(metric_frame, text=metric, font=("Arial", 12, "bold")).pack()
            
            # Right team
            team2_frame = tk.Frame(row_frame, width=300)
            team2_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            tk.Label(team2_frame, text=str(team2_val), font=("Arial", 14)).pack(side=tk.RIGHT, padx=10)
            
            # Add separator
            if i < len(metrics) - 1:
                ttk.Separator(h2h_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Performance metrics tab
        # Create radar chart comparing key performance metrics
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # Define performance categories
        categories = ['Batting\nScore', 'Run\nRate', 'Batting\nS/R', 'Boundaries', 'Bowling\nEconomy', 'Wicket\nTaking']
        
        # Normalize metrics for radar chart (0-1 scale)
        team1_metrics = [
            self.match_data["scoreCard"][0]["runs"] / max(self.match_data["scoreCard"][0]["runs"], self.match_data["scoreCard"][1]["runs"]),
            (self.match_data["scoreCard"][0]["runs"] / float(self.match_data["scoreCard"][0]["overs"])) / 10,  # Normalize run rate (assume max 10)
            (100 * self.match_data["scoreCard"][0]["runs"] / sum(b["balls"] for b in self.match_data["scoreCard"][0]["batsmen"])) / 150,  # Normalize SR (assume max 150)
            sum(b["fours"] + b["sixes"] for b in self.match_data["scoreCard"][0]["batsmen"]) / 30,  # Normalize boundaries (assume max 30)
            1 - (self.match_data["scoreCard"][1]["runs"] / sum(float(b["overs"]) for b in self.match_data["scoreCard"][1]["bowlers"])) / 10,  # Lower economy is better
            sum(b["wickets"] for b in self.match_data["scoreCard"][1]["bowlers"]) / 10  # Normalize wickets (assume max 10)
        ]
        
        team2_metrics = [
            self.match_data["scoreCard"][1]["runs"] / max(self.match_data["scoreCard"][0]["runs"], self.match_data["scoreCard"][1]["runs"]),
            (self.match_data["scoreCard"][1]["runs"] / float(self.match_data["scoreCard"][1]["overs"])) / 10,
            (100 * self.match_data["scoreCard"][1]["runs"] / sum(b["balls"] for b in self.match_data["scoreCard"][1]["batsmen"])) / 150,
            sum(b["fours"] + b["sixes"] for b in self.match_data["scoreCard"][1]["batsmen"]) / 30,
            1 - (self.match_data["scoreCard"][0]["runs"] / sum(float(b["overs"]) for b in self.match_data["scoreCard"][0]["bowlers"])) / 10,
            sum(b["wickets"] for b in self.match_data["scoreCard"][0]["bowlers"]) / 10
        ]
        
        # Cap values between 0 and 1
        team1_metrics = [max(0, min(1, m)) for m in team1_metrics]
        team2_metrics = [max(0, min(1, m)) for m in team2_metrics]
        
        # Number of categories
        N = len(categories)
        
        # Set angle for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the polygon
        
        # Add metrics to complete the polygons
        team1_metrics += team1_metrics[:1]
        team2_metrics += team2_metrics[:1]
        
        # Plot data
        ax.plot(angles, team1_metrics, color='#3498db', linewidth=2, label=team1_name)
        ax.fill(angles, team1_metrics, color='#3498db', alpha=0.3)
        
        ax.plot(angles, team2_metrics, color='#e74c3c', linewidth=2, label=team2_name)
        ax.fill(angles, team2_metrics, color='#e74c3c', alpha=0.3)
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # Configure radar chart
        ax.set_yticks([0.2, 0.4, 0.6, 0.8])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'])
        ax.set_ylim(0, 1)
        
        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        # Add title
        plt.title('Team Performance Comparison', size=14, y=1.1)
        
        # Pack radar chart in performance tab
        radar_frame = tk.Frame(perf_tab)
        radar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Rename the variable to avoid conflict with the scrolling canvas
        figure_canvas = FigureCanvasTkAgg(fig, radar_frame)
        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add text analysis
        text_frame = ttk.LabelFrame(perf_tab, text="Performance Insights", padding=10)
        text_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Build analysis text based on metrics
        winner = team1_name if self.match_data["matchHeader"]["status"].startswith(team1_name) else team2_name
        
        analysis_text = f"""
Match Analysis: {team1_name} vs {team2_name}

• {winner} won the match with a superior overall performance.
• {team1_name if team1_metrics[0] > team2_metrics[0] else team2_name} scored more runs showing better batting performance.
• {team1_name if team1_metrics[2] > team2_metrics[2] else team2_name} had a better batting strike rate.
• {team1_name if team1_metrics[4] > team2_metrics[4] else team2_name} bowled more economically.
• {team1_name if team1_metrics[5] > team2_metrics[5] else team2_name} was more effective at taking wickets.

This analysis is based on key performance metrics normalized across both teams.
        """
        
        analysis_text_widget = scrolledtext.ScrolledText(text_frame, height=10, wrap=tk.WORD)
        analysis_text_widget.pack(fill=tk.BOTH, expand=True)
        analysis_text_widget.insert(tk.END, analysis_text)
        analysis_text_widget.config(state=tk.DISABLED)
        
        # Update the canvas scrollregion after all widgets are added
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def change_match_id(self):
        """Allow user to change match ID and reload data using a dropdown"""
        # Create a custom dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Match ID")
        dialog.geometry("400x250")
        dialog.transient(self.root)  # Make dialog float on top of the main window
        dialog.grab_set()  # Make dialog modal
        dialog.resizable(False, False)
        
        # Configure background
        dialog.configure(bg="#f0f0f0")
        
        # Add some padding
        padding_frame = tk.Frame(dialog, bg="#f0f0f0", padx=20, pady=20)
        padding_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add header
        header_label = tk.Label(
            padding_frame,
            text="Select or Enter Match ID",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        )
        header_label.pack(pady=(0, 20))
        
        # Frame for the dropdown
        dropdown_frame = tk.Frame(padding_frame, bg="#f0f0f0")
        dropdown_frame.pack(fill=tk.X, pady=10)
        
        # Label for the dropdown
        dropdown_label = tk.Label(
            dropdown_frame,
            text="Select Match ID:",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        dropdown_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Predefined match IDs
        match_ids = ["112469", "112462", "112455", "112420", "112402"]
        
        # Add current ID if not in list
        if self.match_id not in match_ids:
            match_ids.insert(0, self.match_id)
            
        # Create StringVar for the dropdown
        selected_id = tk.StringVar(value=self.match_id)
        
        # Create the dropdown
        id_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=selected_id,
            values=match_ids,
            width=15,
            font=("Arial", 12)
        )
        id_dropdown.pack(side=tk.LEFT)
        
        # OR separator
        separator_frame = tk.Frame(padding_frame, bg="#f0f0f0", pady=10)
        separator_frame.pack(fill=tk.X)
        
        left_line = ttk.Separator(separator_frame, orient="horizontal")
        left_line.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        or_label = tk.Label(separator_frame, text="OR", bg="#f0f0f0")
        or_label.pack(side=tk.LEFT, padx=10)
        
        right_line = ttk.Separator(separator_frame, orient="horizontal")
        right_line.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Custom entry frame
        entry_frame = tk.Frame(padding_frame, bg="#f0f0f0")
        entry_frame.pack(fill=tk.X, pady=10)
        
        # Label for custom entry
        entry_label = tk.Label(
            entry_frame,
            text="Enter Custom ID:",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        entry_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry for custom match ID
        custom_entry = ttk.Entry(entry_frame, width=15, font=("Arial", 12))
        custom_entry.pack(side=tk.LEFT)
        custom_entry.insert(0, self.match_id)
        
        # Button frame
        button_frame = tk.Frame(padding_frame, bg="#f0f0f0", pady=20)
        button_frame.pack(fill=tk.X)
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Function to handle dialog submission
        def on_submit():
            # Get the ID from dropdown or entry
            new_id = custom_entry.get().strip() if custom_entry.get().strip() else selected_id.get()
            
            # Check if ID is valid and different
            if new_id and new_id != self.match_id:
                self.match_id = new_id
                # Update the match ID button text in the sidebar
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Frame) and widget.winfo_width() == 200:  # Sidebar
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Button) and "Match ID" in child.cget("text"):
                                child.config(text=f"Change Match ID ({self.match_id})")
                                break
                # Fetch new data
                self.fetch_data()
            
            # Close the dialog
            dialog.destroy()
        
        # Submit button
        submit_button = ttk.Button(
            button_frame,
            text="Load Match",
            command=on_submit
        )
        submit_button.pack(side=tk.RIGHT, padx=10)
        
        # Bind enter key to submit
        dialog.bind("<Return>", lambda event: on_submit())
        
        # Center the dialog on the parent window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set focus on the dropdown
        id_dropdown.focus_set()
        
        # Wait for the dialog to be closed
        dialog.wait_window()


if __name__ == "__main__":
    root = tk.Tk()
    app = CricketDashboard(root)
    root.mainloop()