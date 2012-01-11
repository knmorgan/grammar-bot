import json, twitter, time, math, sys, string

TERMS_PER_SEARCH = 10
HOURLY_LIMIT = 100
MIN_SLEEP_TIME = 10

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
# creds = file_to_object("credentials.json")
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

rate_start_time = 0
rate_end_time = 0
loops = 0
api_calls = 0

start_time = time.time()



# Start the loop that looks for status updates
while 1:
	# We've past our reset time, restart the rate limiting!
	if rate_end_time < time.time():
		rate_start_time = time.time()
		rate_end_time = rate_start_time + (60 * 60)
		api_calls = 1

	# Search for tweets {TERMS_PER_SEARCH} tweets at a time
	for i in range(0, int(1 + len(keys) / TERMS_PER_SEARCH)):
		# Get the begin and end range for the dictionary
		begin = i * TERMS_PER_SEARCH
		end = begin + TERMS_PER_SEARCH - 1
		query = quote_join( keys[begin : end], " OR ")
		# Place the API Call
		results = api.GetSearch(term=query, per_page=15)
		for tweet in reversed(results):
			# print tweet.text
			if tweet.created_at_in_seconds < start_time:
				continue

			# Find the correction object {find:replace:}
			entry = find_correction(tweet.text, corrections)
			if not entry:
				continue
			if entry['find'] not in last_times:
				last_times[entry['find']] = 0
			# If this entry is after the last one that we processed with this key
			# then we'll use it, otherwise skip it
			if tweet.created_at_in_seconds > last_times[entry['find']]:
				text = entry["replace"]["text"]
				type = entry["replace"]["type"]
				new_tweet = "@" + tweet.user.screen_name + " Bro, I think you meant \""
				new_tweet += text + "\""
				if type == "spelling":
					new_tweet +=  " because \"" + entry["find"] + "\" isn't a word."
				elif type == "grammar":
					new_tweet += " because \"" + entry["find"] + "\" is gramatically incorrect."
				pending_tweets.append({
					"id": tweet.id,
					"message": new_tweet
				})
				last_times[entry["find"]] = tweet.created_at_in_seconds
	
	# Loop through all the pending tweets and post them as status updates
	while len(pending_tweets):
		tweet = pending_tweets.pop()
		api.PostUpdate(status=tweet["message"], in_reply_to_status_id=tweet["id"])
		print tweet
		api_calls += 1

	loops += 1

	# Determine the amount of time we need to sleep dynamically, based
	# on the average amount of api calls made per loop and the amount
	# of api calls before we get a limit reset
	time_left = rate_end_time - time.time()
	calls_left = HOURLY_LIMIT - api_calls
	average_calls_per_loop = (api_calls / float(loops))

	print str(api_calls) + " API calls made (" + str(calls_left) + " calls remaining, " + str(average_calls_per_loop) + " calls per loop)"
	
	# Take the maximum of time_to_sleep and MIN_SLEEP_TIME
	time_to_sleep = time_left * average_calls_per_loop / calls_left
	if time_to_sleep < MIN_SLEEP_TIME:
		time_to_sleep = MIN_SLEEP_TIME
	

	print "Sleeping for " + str(time_to_sleep) + " seconds (" + str(time_left / 60 / 60) + " hours left)"
	time.sleep(time_to_sleep)



