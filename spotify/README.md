### Spotify CLI Utilities Documentation

This command-line tool helps you manage your Spotify tracks and playlists. You can export existing playlists or your liked tracks into text files, or populate a Spotify playlist directly from a local text file.

By default, the script creates and works within a local directory named `files`.

* * *

### 🛠 Prerequisites & Setup

To use this tool, you must create a developer application with Spotify to get your API keys:

1.  Log in to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2.  Click **Create an App**, fill in the details, and open your new app's settings.
3.  Note down your **Client ID** and **Client Secret**.
4.  In the app settings, add a **Redirect URI** (e.g., `http://localhost:8080`) and save changes.

* * *

### 🚀 How to Run the Script

The script requires three global authentication arguments followed by a specific operational mode (`subcommand`).

### Global Syntax:

bash

    python main.py <client_id> <client_secret> <redirect_url> <mode> [mode_arguments]
    



* * *

### 📂 Operating Modes & Examples

### 1\. Export a Playlist (`export_playlist_id`)

Extracts all tracks from a specific Spotify playlist and writes them to a text file.

*   **Required parameters:** `playlist_id` and `text_file_name`

**Example Command:**

bash

    python main.py YOUR_CLIENT_ID YOUR_SECRET http://localhost:8080 export_playlist_id 37i9dQZF1DXcBWIGv269mS my_playlist
    



### 2\. Export Favorite Tracks (`export_liked_tracks`)

Backs up your entire "Liked Songs" library from Spotify.

*   **Required parameters:** None. (The underlying function handles the saving process automatically).

**Example Command:**

bash

    python main.py YOUR_CLIENT_ID YOUR_SECRET http://localhost:8080 export_liked_tracks
    



### 3\. Import Tracks from a Text File (`import_text_file`)

Reads a local text file containing song details and adds them to a specified Spotify playlist.

*   **Required parameters:** `text_file_name` and `playlist_id`

**Example Command:**

bash

    python main.py YOUR_CLIENT_ID YOUR_SECRET http://localhost:8080 import_text_file tracks_to_upload 37i9dQZF1DXcBWIGv269mS
    



* * *

### ❓ Getting Help

If you forget the parameter order or want to see all available commands, append `--help` to your script execution:

bash

    python main.py --help
    



You can also get help for a specific mode to see its exact required arguments:

bash

    python main.py YOUR_CLIENT_ID YOUR_SECRET http://localhost:8080 import_text_file --help
    

