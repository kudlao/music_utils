
import os
from utils import import_from_text_file, export_playlist_id, export_liked_tracks, get_spotify
import argparse

parser = argparse.ArgumentParser(
    description="Utils for Spotify"
)

parser.add_argument("client_id", type=str, help="client_id в developer app")
parser.add_argument("client_secret", type=str, help="client_secret в developer app")
parser.add_argument("redirect_url", type=str, help="redirect_url в developer app")
subparsers = parser.add_subparsers(dest="mode", required=True, help="Operating modes")

parser_export_playlist = subparsers.add_parser("export_playlist_id", help="Export playlist from Spotify")
parser_export_playlist.add_argument("playlist_id", type=str, help="playlist_id in spotify")
parser_export_playlist.add_argument("text_file_name", type=str, help="File name txt")

parser_liked = subparsers.add_parser("export_liked_tracks", help="Export favorite tracks from Spotify")
parser_import = subparsers.add_parser("import_text_file", help="Import from text file")
parser_import.add_argument("text_file_name", type=str, help="File name txt")
parser_import.add_argument("playlist_id", type=str, help="playlist_id in spotify")

args = parser.parse_args()
print(f"Mode selected: {args.mode}")
print(f"Client ID: {args.client_id}")

if __name__ == '__main__':
    creds = {'client_id': args.client_id,
    'client_secret': args.client_secret,}
    redirect_url = args.redirect_url
    mode = args.mode

    sp = get_spotify(creds = creds, redirect_url = redirect_url)
    os.makedirs('files', exist_ok=True)

    if mode == 'export_playlist_id':
        print(f"Export playlist ID: {args.playlist_id}")
        export_playlist_id(sp = sp, playlist_id=args.playlist_id, file_name=args.text_file_name)
    elif mode == 'export_liked_tracks':
        print("Export favorite tracks from Spotify...")
        export_liked_tracks(sp= sp)
    elif mode == 'import_text_file':
        print(f"Import file: {args.text_file_name}")
        import_from_text_file(sp, file_name=args.text_file_name, playlist_id=args.playlist_id )

