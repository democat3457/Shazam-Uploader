import math
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from datetime import datetime
import csv
import json
import re
from tqdm import tqdm

load_dotenv()

with open('tables/ZTAGMO.csv') as f:
    reader = csv.DictReader(f)
    shazam_data = list(reader)

# ZDATE is in Core Data time: https://www.epochconverter.com/coredata
# UNIX time + 978307200 seconds = Core Data time
shazam_data.sort(key=lambda x: x['ZDATE'])

print(f'Found {len(shazam_data)} tracks')

scopes = [
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "playlist-modify-public",
]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))

user_id: str = sp.me()['id']

today = datetime.now().date()
playlist_name = f'Shazam Tracks {today.strftime("%Y-%m-%d")}'

track_uris: list[str] = []

for track in tqdm(shazam_data):
    track_name = track["ZTRACKNAME"]
    track_name = re.sub(r"\(((?!feat.? )(?!Remix).)*\)", "", track_name).strip()
    artist_name = track["ZSUBTITLE"]

    search = sp.search(f'{track_name} {artist_name}', limit=20, type='track')["tracks"]["items"]

    for item in search:
        # item["album"] = { "id", "images", "name", "release_date", "release_date_precision", "uri" }
        # item["artists"] = [ { "id", "name", "uri" } ]
        # item["duration_ms"] = int
        # item["id"] = str
        # item["name"] = str
        # item["popularity"] = int
        # item["uri"] = str

        # TODO: validate at least somewhat correct track title and artist(s)
        # TODO: fix Livin' la Vida Loca and Livin' la Vida Loca (Spanish Version) (both by Ricky Martin)

        if item["uri"] in track_uris:
            print(f'WARN: found duplicate track uri, skipping; name "{track_name}" artist "{artist_name}"')
            break

        track_uris.append(item["uri"])
        break

playlist_id = sp.user_playlist_create(user_id, playlist_name)['id']

# limited to 100 tracks per request
for i in range(math.ceil(len(track_uris) / 100)):
    sp.playlist_add_items(playlist_id, track_uris[i*100:(i+1)*100])

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], "-", track['name'])

# print(sp.me())
