# This is a search tool and playlist manager for Spotify
# It allows you to perform more advanced searches on your
# owned playlists, which allows you to more efficiently sort
# your music.
#
# Example - You want to sort your liked songs for hip hop
# music. This is not possible in Spotify, so you select your
# liked songs playlist, and enter the search term for hip hop.
# You can then create a playlist from these results, or further
# refine it, to remove any unfavourable results. You can use
# negative search to remove any tracks from results that have
# A$AP Rocky as an artist for example.
#
# Requires three environment variables to be set -
# SPOTIPY_CLIENT_ID
# SPOTIPY_CLIENT_SECRET
# SPOTIPY_REDIRECT_URI
import os
import sys
# import json
import spotipy
# import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

def get_int_range(min, max, prompt="Enter your selection: "):
    list_selection = -2
    while (list_selection < min or list_selection > max):
        try:
            list_selection = int(input(prompt))
            print()
            return list_selection
        except ValueError:
            continue

def print_playlists(playlist_paging_object):
    print()
    print("0 \t Quit Program")
    i = 1
    for playlist in playlist_paging_object['items']:
        print(i, '\t', playlist['name'])
        i += 1
    num_playlists = len(playlist_paging_object['items']) + 1
    print(num_playlists, '\t', "Liked Songs\n")

def build_track_id_list(track_object_list):
    track_ids = []
    for track in track_object_list:
        track_uris.append(track['id'])
    return track_ids

def current_user_save_tracks_arbitrary(so, track_ids, num_requests):
    for i in range(num_requests):
        so.current_user_saved_tracks_add(
                track_ids[i*100:(i+1)*100])
    so.current_user_saved_tracks_add(
            track_ids[num_requests*100:])
    print("\nSaved", len(track_ids), "results to Liked Songs")

# Get the username from terminal
username = sys.argv[1]
scope = 'user-library-read playlist-modify-public playlist-modify-private'
# User ID: bmcfadden

# Erase cache and prompt for user permission
# NOTE: Omitting this step leaves a .cache{username} file in cd
try:
    token = util.prompt_for_user_token(username, scope)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

# Create our Spotify object
spotify_object = spotipy.Spotify(auth=token)
user = spotify_object.current_user()
# print(json.dumps(user, sort_keys=True, indent=4))

# Main Menu Loop
while True:
    playlists = spotify_object.user_playlists(username)
    print_playlists(playlists)
    num_playlists = len(playlists['items'])

    # Menu selection
    print("\nThere are", num_playlists, "playlists.")
    print("Select a playlist by number.")
    list_selection = get_int_range(0, num_playlists)

    # Handle an early exit from the application
    if (list_selection == 0):
        print("Good-bye")
        quit(0)

    # Build a list of every track
    selection_name = ""
    playlist = None
    all_tracks = []
    iter = []

    # Private library: 50 track limit per request
    # can get number from current_user_saved_tracks()['total']
    if (list_selection == num_playlists):
        selection_name = "Liked Songs"
        iter = spotify_object.current_user_saved_tracks(50, 0)

    # Public playlist: 100 track limit per request
    else:
        iter = spotify_object.user_playlist_tracks(
        playlists['items'][list_selection - 1]['owner']['id'],
        playlists['items'][list_selection - 1]['id'])
        selection_name = playlists['items'][list_selection - 1]['name']

    # Build complete track list
    while (iter != None):
        for track in iter['items']:
            all_tracks.append(track['track'])
        iter = spotify_object.next(iter)

    # Filter loop
    while True:
        print()
        for i in range(1, len(all_tracks)):
            print(i, '\t', all_tracks[i]['name'], "by",
                    all_tracks[i]['artists'][0]['name'])
        playlist_selection = list_selection

        print('\n', selection_name, "by", user['display_name'],
                "[", len(all_tracks), "tracks ].")
        print("\nWhat do you want to do with it?")
        print("0 \tSave Tracks to Playlist")
        print("1 \tFilter By Genre")
        print("2 \tFilter By Artist")
        print("3 \tFilter By Track Number")
        print("4 \tUnfollow/Delete Playlist,\n")

        NUM_OPTIONS = 4
        list_selection = get_int_range(0, NUM_OPTIONS)

        if (list_selection == 0):
            break
        if (list_selection == 4):
            spotify_object.user_playlist_unfollow(
                    playlists['items'][playlist_selection - 1]['owner']['id'],
                    playlists['items'][playlist_selection - 1]['id'])
            break
        # Get negative/positive search and filter
        sieve = input("Enter the term to filter by(-prefix for negative search:")
        positive_search = True
        if sieve[0] == '-':
            positive_search = False
            sieve = sieve[1:]
        filtered_list = []
        # Filter by genre
        if (list_selection == 1):
            sieve = sieve.lower()
            for track in all_tracks:
                artist_genres = spotify_object.artist(
                        track['artists'][0]['id'])['genres']
                match_flag = False
                for genre in artist_genres:
                    if sieve == genre:
                        match_flag = True
                        if positive_search == True:
                            filtered_list.append(track)
                            break
                if positive_search == False and match_flag == False:
                    filtered_list.append(track)
        # End filter by genre
        elif (list_selection == 2):
            for track in all_tracks:
                match_flag = False
                for artist in track['artists']:
                    if sieve == artist['name']:
                        match_flag = True
                        if positive_search == True:
                            filtered_list.append(track)
                            break
                if positive_search == False and match_flag == False:
                    filtered_list.append(track)
        # End filter by artist
        elif (list_selection == 3):
            track_selection = -1
            while (track_selection < 1 or track_selection > len(all_tracks) + 1):
                try:
                    track_selection = int(sieve)
                    continue
                except ValueError:
                    sieve = input("Enter the term to filter by(-prefix for negative search:")
                    positive_search = True
                    if sieve[0] == '-':
                        positive_search = False
                    sieve = sieve[1:]
            for i in range(len(all_tracks)):
                match_flag = False
                if track_selection-1 == i:
                    match_flag = True
                    if positive_search == True:
                        filtered_list.append(all_tracks[i])
                        break
                if positive_search == False and match_flag == False:
                    filtered_list.append(all_tracks[i])
        # End filter by track number
        all_tracks = None
        all_tracks = filtered_list
    #End filter loop

    if (len(all_tracks) == 0):
        print("No results, returning to main menu.\n")
        continue
    if (list_selection == 4):
        print("Playlist successfully deleted.\n")
        continue

    #Result options:
    NUM_OPTIONS = 3
    print("\n0 \tReturn to main menu")
    print("1 \tAdd all results to library")
    print("2 \tMake a new playlist with results")
    print("3 \tAdd songs to an existing playlist")
    print()

    list_selection = get_int_range(0, NUM_OPTIONS)

    #[0] Quit the application
    if (list_selection == 0):
        continue
    #[1] Add all songs to library
    elif (list_selection == 1):
        track_uris = build_track_id_list(all_tracks)
        num_requests = int(len(track_uris) / 100)
        current_user_save_tracks_arbitrary(spotify_object, track_uris, num_requests)
    #[2] Make a new playlist, and add results to it
    elif (list_selection == 2):
        new_playlist_name = input("Enter a name for the new playlist:")
        new_playlist_description = input("Enter a description of the playlist:")
        new_playlist = spotify_object.user_playlist_create(user['id'],
                new_playlist_name, True, new_playlist_description)
        print("\nCreated new playlist", new_playlist_name)
        track_uris = build_track_id_list(all_tracks)
        num_requests = int(len(track_uris) / 100)

        ### TODO: Replace with function
        for i in range(num_requests):
            spotify_object.user_playlist_remove_all_occurrences_of_tracks(
                    user['id'], new_playlist['id'], track_uris[i*100:(i+1)*100])
            spotify_object.user_playlist_add_tracks(user['id'],
                    new_playlist['id'], track_uris[i*100:(i+1)*100])
        spotify_object.user_playlist_remove_all_occurrences_of_tracks(
                user['id'], new_playlist['id'], track_uris[num_requests*100:])
        spotify_object.user_playlist_add_tracks(user['id'], new_playlist['id'],
                track_uris[num_requests*100:])
        print("\nSaved", len(track_uris), "results to", new_playlist_name)

    #[3] Add songs to existing playlist
    elif (list_selection == 3):
        print_playlists(playlists)
        num_playlists = len(playlists['items'])
        # Menu selection
        print("\nThere are", num_playlists, "playlists.")
        print("Select a playlist by number.")
        list_selection = get_int_range(0, num_playlists)

        # Handle an early exit from the application
        if (list_selection == 0):
            print("Good-bye")
            quit(0)

        track_uris = build_track_id_list(all_tracks)
        num_requests = int(len(track_uris) / 100)

        # Add songs to liked songs
        if (list_selection == num_playlists):
            current_user_save_tracks_arbitrary(spotify_object, rack_uris, num_requests)
        # Add songs to other playlist
        else:
            ## TODO: replace with function
            for i in range(num_requests):
                spotify_object.user_playlist_remove_all_occurrences_of_tracks(
                        user['id'], playlists['items'][list_selection-1]['id'],
                        track_uris[i*100:(i+1)*100])
                spotify_object.user_playlist_add_tracks(user['id'],
                        playlists['items'][list_selection-1]['id'],
                        track_uris[i*100:(i+1)*100])
            spotify_object.user_playlist_remove_all_occurrences_of_tracks(
                    user['id'], playlists['items'][list_selection-1]['id'],
                    track_uris[num_requests*100:])
            spotify_object.user_playlist_add_tracks(user['id'],
                    playlists['items'][list_selection-1]['id'],
                    track_uris[num_requests*100:])
            print("Saved", len(track_uris), "results to",
                    playlists['items'][list_selection-1]['name'], "\n")
    # end add songs to a playlist
# end main application loop
