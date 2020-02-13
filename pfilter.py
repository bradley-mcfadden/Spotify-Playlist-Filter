import os
import spotipy
import spotipy.util as util

# Filter a track by its artist's genre. Sometimes might not yield
# expected results. Example: You only want rap songs, but Mac Miller
# appears on a pop song.
# track		Track object to filter on
# term		Genre to perform comparisons with
# pstve		Perform a postive or a negative search
# -> ret	True or false if track matches search term
def genre_filter(track, term, pstve=True):
	genres = spot.artist(track['artists'][0]['id'])['genres']
	match = False
	for genre in genres:
		if term == genre:
			match = True
			if pstve == True:
				return True
	if pstve == False and match == False
		return True
	return False


# Filter a track by its artists.
# track		Track object to filter on
# term		Artist name to perform comparisons with
# pstve		Perform a positive or negative search
# -> ret	True or false if track matches search term
def artist_filter(track, term, pstve=True):
	match = False
	for artist in track['artists']:
		if term == artist['name']:
			match = True
			if pstve == True:
				return True
	if pstve == False and match == False:
		return True
	return False	


# Perform a set subtraction operation on the result set and the tracks
# tracks	Array of tracks to subtract from results
def exclude_from_results(tracks):
	self.results = list(set(self.results) - set(tracks))


# Wrapper for spotipy objects that makes it easier to use
class PFilter:
	scope = 'user-library-read playlist-modify-public playlist-modify-private'
	def __init__(self, username):
		try:
			self.token = util.prompt_for_user_token(username, scope)
		except:
			os.remove(f".cache-{username}")
			self.token = util.prompt_for_user_token(username, scope)
		self.spot = spotipy.Spotify(auth=token)
		self.user = spot.current_user()
		self.playlists = []
		self.results = []


	# Return a list of all playlist paging objects
	# -> ret	List of playlist paging objects
	def user_playlists(self):
		playlists = []
		it = self.spot.current_user_playlists()
		while (it != None):
			playlists += it['items']
			it = spot.next(it)
		return playlists    


	# Get all user's saved tracks from library
	# WARNING: Can be very slow, do not call often.
	# -> ret	List of track paging objects from library
	def user_saved_tracks(self):
		saved_tracks = []
		it = self.spot.current_user_saved_tracks()
		while (it != None):
			saved_tracks += it['items'] 
			it = spot.next(it)
		return saved_tracks    
          

	# Get a list of tracks from a playlist
	# playlist_id	URI of playlist
	# -> ret		List of track paging objects from playlist
	def user_playlist_tracks(self, playlist_id):
		playlist_tracks = []
		it = spot.user_playlist_tracks(self.user['id'], playlist_id)
		while (it != None):
			playlist_tracks += it['items']
			it = spot.next(it)
		return saved_tracks    


	# Create a new playlist
	# title		Title of new playlist
	# desc		Description of new playlist
	# -> ret	Paging object of new playlist
	def create_playlist(self, title, desc):
		new_playlist = spot.user_playlists_create(self.user['id'], title, True, desc)
		return new_playlist['id']       
	

	# Take in array of track objects and add them to the playlist
	# - playlist_id Playlist to add tracks to
	# - tracks		Array of track objects to add to playlist
    def playlist_add_tracks(self, playlist_id, tracks):
		track_ids = track['id'] for track in tracks
		num_requests = len(track_uris) // 100
		for i in range(num_requests):
			spot.user_playlist_remove_all_occurrences_of_tracks(self.user['id'],playlist_id, track_ids[i*100:(i+1)*100])
			spot.user_playlist_add_tracks(self.user['id'], playlist_id, track_ids[i*100:(i+1)*100])
		spot.user_playlist_remove_all_occurrences_of_tracks(self.user['id'], playlist_id, track_ids[num_requests*100:])
		spot.user_playlist_add_tracks(self.user['id'], playlist_id, track_ids[num_requests*100:])


	# Set the result set to something else
	# tracks	List of track paging objects to update with
    def set_results(self, tracks):
        self.results = tracks


	# Reduce the result set with a filter function
	# term		Search term for fitler function
	# pstve		Perform a postive or negative search
	# flter		Filter function to apply to each track paging object
	# -> ret	Updated list of track objects
    def filter_results(self, term, pstve=True, flter=genre_filter):
		self.results = [track for track in self.results if flter(track, term, pstve)]
		return self.results        


	# Unfollow some playlist
	# playlist_id	List ID of the playlist you want to unfollow
    def unfollow_playlist(self, playlist_id):
		spot.user_playlist_unfollow(self.user['id'], playlist_id)        
