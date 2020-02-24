import os
import spotipy
import spotipy.util as util
import sys

# Wrapper for spotipy objects that makes it easier to use
class PFilter:
	scope = 'user-library-read playlist-modify-public playlist-modify-private'
	def __init__(self, username):
		try:
			self.token = util.prompt_for_user_token(username, PFilter.scope)
		except:
			os.remove(f".cache-{username}")
			self.token = util.prompt_for_user_token(username, PFilter.scope)
		self.spot = spotipy.Spotify(auth=self.token)
		self.user = self.spot.current_user()
		self.playlists = []
		self.results = []


	# Return a list of all playlist paging objects
	# -> ret	List of playlist paging objects
	def user_playlists(self):
		playlists = []
		it = self.spot.current_user_playlists()
		while (it != None):
			playlists += it['items']
			it = self.spot.next(it)
		return playlists    


	# Get all user's saved tracks from library
	# WARNING: Can be very slow, do not call often.
	# -> ret	List of track paging objects from library
	def user_saved_tracks(self):
		saved_tracks = []
		it = self.spot.current_user_saved_tracks()
		while (it != None):
			# saved_tracks += it['items'] 
			[saved_tracks.append(trk['track']) for trk in it['items']]
			it = self.spot.next(it)
		return saved_tracks    
          

	# Get a list of tracks from a playlist
	# playlist_id	URI of playlist
	# -> ret		List of track paging objects from playlist
	def user_playlist_tracks(self, playlist_id):
		playlist_tracks = []
		it = self.spot.user_playlist_tracks(self.user['id'], playlist_id)
		while (it != None):
			# playlist_tracks += it['items']
			[playlist_tracks.append(trk['track']) for trk in it['items']]
			it = self.spot.next(it)
		return playlist_tracks 


	# Create a new playlist
	# title		Title of new playlist
	# desc		Description of new playlist
	# -> ret	Paging object of new playlist
	def create_playlist(self, title, desc):
		new_playlist = self.spot.user_playlist_create(self.user['id'], title, True, desc)
		return new_playlist['id']       
	

	# Take in array of track objects and add them to the playlist
	# - playlist_id Playlist to add tracks to
	# - tracks		Array of track objects to add to playlist
	def playlist_add_tracks(self, playlist_id, tracks):
		track_ids = [track['id'] for track in tracks]
		num_requests = len(track_ids) // 100
		for i in range(num_requests):
			self.spot.user_playlist_remove_all_occurrences_of_tracks(self.user['id'],playlist_id, track_ids[i*100:(i+1)*100])
			self.spot.user_playlist_add_tracks(self.user['id'], playlist_id, track_ids[i*100:(i+1)*100])
		self.spot.user_playlist_remove_all_occurrences_of_tracks(self.user['id'], playlist_id, track_ids[num_requests*100:])
		self.spot.user_playlist_add_tracks(self.user['id'], playlist_id, track_ids[num_requests*100:])


	# Set the result set to something else
	# tracks	List of track paging objects to update with
	def set_results(self, tracks):
		self.results = tracks


	# Reduce the result set with a filter function
	# term		Search term for fitler function
	# pstve		Perform a postive or negative search
	# flter		Filter function to apply to each track paging object
	# -> ret	Updated list of track objects
	def filter_results(self, term, pstve, flter):
		self.results = [track for track in self.results if flter(track, term, pstve)]
		return self.results        


	# Unfollow some playlist
	# playlist_id	List ID of the playlist you want to unfollow
	def unfollow_playlist(self, playlist_id):
		self.spot.user_playlist_unfollow(self.user['id'], playlist_id) 

   
	# Filter a track by its artist's genre. Sometimes might not yield
	# expected results. Example: You only want rap songs, but Mac Miller
	# appears on a pop song.
	# track		Track object to filter on
	# term		Genre to perform comparisons with
	# pstve		Perform a postive or a negative search
	# -> ret	True or false if track matches search term
	def genre_filter(self, track, term, pstve=True):
		genres = self.spot.artist(track['artists'][0]['id'])['genres']
		match = False
		for genre in genres:
			if term == genre:
				match = True
				if pstve == True:
					return True
		if pstve == False and match == False:
			return True
		return False


	# Filter a track by its artists.
	# track		Track object to filter on
	# term		Artist name to perform comparisons with
	# pstve		Perform a positive or negative search
	# -> ret	True or false if track matches search term
	def artist_filter(self, track, term, pstve=True):
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
	def exclude_from_results(self, tracks):
		self.results = list(set(self.results) - set(tracks))


if __name__ == "__main__":
	user = input("Enter your spotify id: ")
	pf = PFilter(user)
	while True: # while01
		
		libchoice = None
		while not libchoice:
			libprompt = input("Do you want to use your playlists or library? (playlist/library/Q!): ")
			libchoice = libprompt if (libprompt == "playlist" or libprompt == "library" or libprompt == "Q!") else None
		# endwhile
		if libchoice == "playlist":
			plists = pf.user_playlists()
			[print('*', '\t', plist['name']) for plist in plists]
			pchoice = None
			while not pchoice: # while02 
				pprompt = input("\nSelect a playlist by name (Q! to quit):" )
				if (pprompt == "Q!"):
					sys.exit(0)
				pchoice = [p for p in plists if p['name'] == pprompt]
			# endwhile02
			pchoice = pchoice[0]
			print(pchoice['name'])

			trks = pf.user_playlist_tracks(pchoice['id'])
		elif libchoice == "library":
			trks = pf.user_saved_tracks()
		else:
			sys.exit(0)
		# endif

		[print('$', '\t', trk['name'][:24], " by ", trk['artists'][0]['name'], 
		" on ", trk['album']['name'][:24]) for trk in trks]

		pf.set_results(trks)

		while True: # while03
			print("\nWhat do you want to do with the results?")			
			print(">0\tStop Filtering")
			print(">1\tFilter by Genre")
			print(">2\tFilter by Artist")
			print(">3\tUnfollow Playlist")
			print(">4\tFilter by Name")
			NUM_OPS = 5
			fchoice = -1 
			while fchoice < 0 or fchoice > 4: # while04
				try:
					fchoice = int(input("Select your option: "))
					break	
				except ValueError:
					continue
			# endwhile04
			
			# if01
			if fchoice == 0:
				break
			# endif01

			ptv_prompt = None
			while ptv_prompt != "pos" and ptv_prompt != "neg": # while05
				ptv_prompt = input("pos/neg search?: ")
			# endwhile05

			ptv_search = True if ptv_prompt == "pos" else False
			
			s_term = input("Enter a search term: ")
			
			# if02
			results = []
			if fchoice == 1:
				results = pf.filter_results(s_term, ptv_search, pf.genre_filter)
			elif fchoice == 2:
				results = pf.filter_results(s_term, ptv_search, pf.artist_filter)
			elif fchoice == 3:
				pf.unfollow_playlist(pchoice['id'])
				break
			else: # fchoice == 4:
				results = pf.filter_results(s_term, ptv_search, lambda track, term, ptv : ((track['name'] == term) == ptv))
			# endif02
			pf.set_results(results)
			trks = pf.results
			[print('$', '\t', trk['name'][:24], " by ", trk['artists'][0]['name'], 
			" on ", trk['album']['name'][:24]) for trk in trks]
		# endwhile03

		print("\nWhat do you want to do with these tracks?")
		print("%0> Nothing. Continue onward.")
		print("%1> Create a new playlist.")
		print("%2> Add results to an existing playlist.")
		
		NUM_OPS2 = 3
		dchoice = -1
		while dchoice < 0 or dchoice >= NUMOPS: # while05
			try:
				dchoice = int(input("Enter your choice: "))
				break
			except ValueError:
				continue
		# endwhile05

		# if03
		if dchoice == 0:
			continue
		elif dchoice == 1:
			np_name = input("Enter the name of the new playlist: ")
			np_desc = input("Enter the description of the new playlist: ")
			pf.playlist_add_tracks(pf.create_playlist(np_name, np_desc), pf.results)	
		else: # dchoice == 2:
			pchoice = None
			while not pchoice: # while06 
				pprompt = input("\nSelect a playlist by name:" )
				if (pprompt == "Q!"):
					sys.exit(0)
				pchoice = [p for p in plists if p['name'] == pprompt]
			# endwhile06
			pf.playlist_add_tracks(pchoice[0]['id'], pf.results)
	# endwhile01
# end program
