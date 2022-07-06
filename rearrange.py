import spotipy
import config
import requests

import pprint
import time
import os

os.system("cls" if os.name == "nt" else "clear")

def get_playlist_music_list(music_iter):
    """Returns a list with formated music labels from a iterable with Spotify musics."""
    music_list = []
    for music in music_iter:
        music = music["track"]
        music_label = music["artists"][0]["name"] + " - "
        album_release_date = music["album"]["release_date"]
        if music["album"]["release_date_precision"] == "year":
            album_release_date += "-01-01"
        elif music["album"]["release_date_precision"] == "month":
            album_release_date += "-01"
        music_label += album_release_date + " - "
        music_label += music["album"]["name"] + " - "
        music_label += str(music["disc_number"]).zfill(6) + " - " #I don't know if there's a better solution for that :P
        music_label += str(music["track_number"]).zfill(6) + " - " 
        music_label += music["name"] 
        music_list.append(music_label)
    return music_list

#These next ugly lines were made because the lib starts to erroring
#out whenever spotify returns a 50X or 429 response code in the
#playlist reorder method. When they fix that or wathever, I remove this.
session = requests.Session()
class SpotifyFixed(spotipy.Spotify):
    def playlist_reorder_items(
        self,
        playlist_id,
        range_start,
        insert_before,
        range_length = 1,
        snapshot_id = None
    ):
        plid = self._get_id("playlist", playlist_id)
        payload = {
            "range_start": range_start,
            "range_length": range_length,
            "insert_before": insert_before
        }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        headers = self._auth_headers()
        while True:
            response = session.put(f"https://api.spotify.com/v1/playlists/{plid}/tracks",
                                    headers = headers,
                                    json = payload)
            if response.status_code == 200:
                break
            else:
                continue
        return response.json()

os.environ["SPOTIPY_CLIENT_ID"] = config.SPOTIPY_CLIENT_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = config.SPOTIPY_CLIENT_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = "https://127.0.0.1:9090"
sp = SpotifyFixed(
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope = ("playlist-read-collaborative", "playlist-modify-public",
                 "playlist-read-private", "playlist-modify-public")
    )
)
user_data = sp.me()

print(f"I've logged into Spotify as user {user_data['display_name']} with id {user_data['id']}\n")
user_playlists = sp.current_user_playlists(limit = None)["items"]
for item in user_playlists[:]:
    if item["owner"]["id"] != user_data["id"]:
        user_playlists.remove(item)
print("These are the playlists owned by you:")
print("\n".join([f"{user_playlists.index(playlist)}. {playlist['name']} - {playlist['id']}" for playlist in user_playlists]))
while True:
    try:
        playlist = user_playlists[int(input("\nPlease insert the number corresponding to the playlist you want to edit: "))]
    except:
        print("You haven't inserted a valid playlist number!")
    else:
        break

print(f"You have chosen the {playlist['name']} playlist. The musics contained in the playlist will be fetched now...")
playlist_musics = sp.playlist_items(playlist["id"],
                                    fields = "href,limit,next,offset,previous,total,"\
                                    "items(track(album(album_type,id,release_date,"\
                                    "release_date_precision,name,artists),artists"\
                                    "(name,popularity,genre),disc_number,linked_from,"\
                                    "name,track_number))")
if playlist_musics["next"]:
    current_page = playlist_musics.copy()
    while True:
        next_page = sp.next(current_page)
        playlist_musics["items"] += next_page["items"]
        if next_page["next"]:
            corrent_page = next_page.copy()
        else:
            break
print(f"Fetched a total of {len(playlist_musics['items'])} musics.")

music_list = get_playlist_music_list(playlist_musics["items"])
sorted_music_list = sorted(music_list)
for index, music in enumerate(sorted_music_list):
    print(f"{index + 1}. {music}")
confirmation = input("\nAt the end of the process, the playlist will end up sorted this way. Proceed? (y/aything else) ")
if confirmation != "y":
    print("Cancelled operation.")
    exit()

current_pos = 0
while True:
    while current_pos < len(sorted_music_list):
        music = music_list[current_pos]
        new_pos = sorted_music_list.index(music)
        if current_pos == new_pos:
            print(f"{current_pos + 1} -> {new_pos + 1} |||| {music}")
            current_pos += 1
        else:
            sp.playlist_reorder_items(playlist["id"], current_pos, new_pos + 1)        
            time.sleep(1)
            sp.playlist_reorder_items(playlist["id"], new_pos - 1, current_pos)
            time.sleep(1)
            print(f"{current_pos + 1} -> {new_pos + 1} |||| {music}")
            music_list[current_pos], music_list[new_pos] = music_list[new_pos], music_list[current_pos]
    print("Theorically finished sorting. Checking within Spotify to see if all changes were apllied...")
    playlist_musics = sp.playlist_items(playlist["id"],
                                    fields = "href,limit,next,offset,previous,total,"\
                                    "items(track(album(album_type,id,release_date,"\
                                    "release_date_precision,name,artists),artists"\
                                    "(name,popularity,genre),disc_number,linked_from,"\
                                    "name,track_number))")
    if playlist_musics["next"]:
        current_page = playlist_musics.copy()
        while True:
            next_page = sp.next(current_page)
            playlist_musics["items"] += next_page["items"]
            if next_page["next"]:
                corrent_page = next_page.copy()
            else:
                break
    music_list = get_playlist_music_list(playlist_musics["items"])
    if music_list == sorted_music_list:
        print("Process finished. Your playlist is now sorted.")
        break
    else:
        print("Spotify didn't aplly all the changes, so the process will be repeated. Expect it to be much faster now.")
    
