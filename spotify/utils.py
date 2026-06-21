import os
import time
import json
from spotipy.exceptions import SpotifyException
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_spotify(creds: dict, redirect_url: str):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(**creds,
                                                   redirect_uri=redirect_url,
                                                   scope="user-library-read,playlist-modify-private,playlist-modify-public"),
                         retries=0,
                         status_retries=0,
                         requests_timeout=10)
    return sp

def import_from_text_file(sp: spotipy.Spotify, file_name: str, playlist_id: str):
    txt_path = f'files/{file_name}.txt'
    failed_path = 'files/failed_tracks.txt'
    success_log_path = 'files/successful_tracks.txt'

    if not os.path.exists(txt_path):
        print(f"File {txt_path} not found!")
        exit()
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    total_tracks = len(lines)
    print(f"Tracks loaded for processing: {total_tracks}")
    uris = []
    successfully_processed_index = 0
    global_index = 0

    try:
        for cnt, line in enumerate(lines):
            global_index = cnt


            print(f"\rProcessed: {cnt}/{total_tracks} ( Find in batch: {len(uris)} ) | Current: {line[:40]}...", end="", flush=True)

            try:
                time.sleep(1.5)
                search_result = sp.search(q=line, type='track', limit=1)
                tracks = search_result.get('tracks', {}).get('items', [])

                if tracks:
                    track_data = tracks[0]
                    track_uri = track_data['uri']
                    spotify_name = f"{track_data['artists'][0]['name']} - {track_data['name']}"

                    uris.append(track_uri)


                    log_data = {
                        "query": line,
                        "spotify_name": spotify_name,
                        "uri": track_uri
                    }
                    with open(success_log_path, 'a', encoding='utf-8') as f_succ:

                        f_succ.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                else:

                    with open(failed_path, 'a', encoding='utf-8') as f_fail:
                        f_fail.write(f"{line}\n")


                if len(uris) == 100:
                    time.sleep(2.0)
                    sp.playlist_add_items(playlist_id, uris)
                    uris = []
                    successfully_processed_index = cnt
                    print(f"\n\n[SUCCESS] 100 tracks added to playlist. Total number of lines completed.: {cnt}\n")

            except SpotifyException as e:
                successfully_processed_index = cnt - len(uris)
                if e.http_status == 429:
                    print(f"\n\n[RATE LIMIT] Spotify has limited requests. Ending your session...")
                    raise e
                else:
                    raise e

    except Exception as main_error:
        print(f"\n\nThe script was terminated due to an error: {main_error}")

    finally:

        if uris:
            try:
                print(f"\nTrying to save the last batch from {len(uris)} tracks before the end...")
                sp.playlist_add_items(playlist_id, uris)
                successfully_processed_index = global_index
                print("The tail has been successfully saved!")
            except Exception:
                print("Failed to save final batch to playlist (API blocked).")


        remaining_lines = lines[successfully_processed_index:]
        with open(txt_path, 'w', encoding='utf-8') as f_update:
            for r_line in remaining_lines:
                f_update.write(f"{r_line}\n")

        print(f"\n=== Session complete ===")
        print(f"Successfully processed and removed from the original file line: {successfully_processed_index}")
        print(f"There are still lines left to process next time: {len(remaining_lines)}")

def export_liked_tracks(sp: spotipy.Spotify):
    liked_tracks = []
    offset = 0
    limit = 50
    print("Starting to download my favorite tracks....")

    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results.get("items", [])

        if not items:
            break

        for item in items:
            track = item["track"]
            artist_name = track["artists"][0]["name"]
            track_name = track["name"]
            track_uri = track["uri"]
            json_track = dict(spotify_name=f"{artist_name} — {track_name}", spotify_uri=track_uri)
            liked_tracks.append(json.dumps(json_track, ensure_ascii=False))

        offset += limit
        print(f"Tracks uploaded: {len(liked_tracks)}")
    with open(f"files/my_liked_tracks.txt", "w", encoding="utf-8") as f:
        for song in liked_tracks:
            f.write(song + "\n")

    print(f"\nDone! All tracks save in files/my_liked_tracks.txt")

def export_playlist_id(sp: spotipy.Spotify, playlist_id: str, file_name: str):
    playlist_tracks = []
    offset = 0
    limit = 100

    print("Starting to download tracks and their URIs....")

    while True:
        results = sp.playlist_items(
            playlist_id=playlist_id,
            limit=limit,
            offset=offset,
            fields="items(item(uri, name, artists(name)))"
        )
        items = results.get("items", [])

        if not items:
            break

        for item in items:
            track = item.get("item")
            if track:
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                track_name = track["name"]
                track_uri = track["uri"]
                json_track = dict(spotify_name= f"{artists} — {track_name}", spotify_uri= track_uri)
                playlist_tracks.append(json.dumps(json_track, ensure_ascii=False))

        offset += limit
        print(f"Complete tracks: {len(playlist_tracks)}")

    with open(f"files/{file_name}.txt", "w", encoding="utf-8") as f:
        for song in playlist_tracks:
            f.write(song + "\n")

    print(f"\nDone ! List with URI save in {file_name}.txt")
