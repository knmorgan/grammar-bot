import json, twitter, time, math, sys, string

TERMS_PER_SEARCH = 10
HOURLY_LIMIT = 350

# Take a string and find the item in dictionary
def find_correction(str, dictionary):
	string_lower = string.lower(str)
	for key in dictionary.keys():
		if string.find(str, string.lower(key)) >= 0:
			return {
				"find": key,
				"replace": dictionary[key]
			}
	return False

# Take a list and surround each item with quotes, then put them
# together in one string using glue
def quote_join(list, glue):
	str = ""
	for item in list:
		if str:
			str += " OR "
		str += '"' + item + '"'
	return str

# Read a JSON object from a file and return the object
def file_to_object(file_path):
	file = open(file_path, "r")
	str = ""
	for line in file: str += line
	return json.loads(str)

# Load in the credentials config file into credentials dictionary
creds = file_to_object("credentials.local.json")
# Load in the list of corrections
corrections = file_to_object("replacements.json")

# Create the API object with all the credentials
api = twitter.Api(
	consumer_key = creds.get('consumer_key'),
	consumer_secret = creds.get('consumer_secret'),
	access_token_key = creds.get('access_token_key'),
	access_token_secret = creds.get('access_token_secret')
)


keys = corrections.keys()
last_times = {}
pending_tweets = []

rate_limit = api.GetRateLimitStatus()
reset_time = rate_limit["reset_time_in_seconds"]
api_calls = HOURLY_LIMIT - rate_limit["remaining_hits"]
loops = 0

print rate_limit
sys.exit()

# Start the loop that looks for status updates
while api_calls <= 2:
	# The number of API calls in this loop
	api_calls_loop = 0
	# Search for tweets {TERMS_PER_SEARCH} tweets at a time
	for i in range(0, int(1 + len(keys) / TERMS_PER_SEARCH)):
		# Get the begin and end range for the dictionary
		begin = i * TERMS_PER_SEARCH
		end = begin + TERMS_PER_SEARCH - 1
		query = quote_join( keys[begin : end], " OR ")
		# Place the API Call
		results = api.GetSearch(term=query, per_page=15)
		for tweet in results:
			# Find the correction object {find:replace:}
			entry = find_correction(tweet.text, corrections)
			if not entry:
				continue
			if entry['find'] not in last_times:
				last_times[entry['find']] = 0
			# If this entry is after the last one that we processed with this key
			# then we'll use it, otherwise skip it
			if tweet.created_at_in_seconds > last_times[entry['find']]:
				pending_tweets.append("@" + tweet.user.screen_name + " Bro, I think you meant \"" + entry["replace"] + "\"")
				last_times[entry["find"]] = tweet.created_at_in_seconds
	
	# Loop through all the pending tweets and post them as status updates
	while len(pending_tweets):
		tweet = pending_tweets.pop()
		api.PostUpdate(status=tweet)
		api_calls += 1

	# We've past our reset time, restart the rate limiting!
	if reset_time < time.time():
		rate_limit = api.GetRateLimitStatus()
		reset_time = rate_limit["reset_time_in_seconds"]
		api_calls = HOURLY_LIMIT - rate_limit["remaining_hits"]

	loops += 1
	
	# Determine the amount of time we need to sleep dynamically, based
	# on the average amount of api calls made per loop and the amount
	# of api calls before we get a limit reset
	time_left = reset_time - time.time()
	time.sleep(time_left / (api_calls / loops))





