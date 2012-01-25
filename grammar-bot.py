import json, twitter, time, math, sys, string, random, os

SECONDS_BETWEEN_TWEETS = 120

files = {
	"credentials": os.path.dirname(os.path.realpath(__file__)) + "/" + "credentials.json",
	"replacements": os.path.dirname(os.path.realpath(__file__)) + "/" + "replacements.json",
	"tweets": os.path.dirname(os.path.realpath(__file__)) + "/" + "tweets.dat"
}

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


# Load the tweet templates
creds = file_to_object(files["credentials"])

# Create the API object with all the credentials
api = twitter.Api(
	consumer_key = creds.get("consumer_key"),
	consumer_secret = creds.get("consumer_secret"),
	access_token_key = creds.get("access_token_key"),
	access_token_secret = creds.get("access_token_secret")
)


tweets = []
last_modified_time = 0

while 1:
	try:
		# Find the time of the most recently modified file
		modified_time = 0
		for file_path in files.values():
			modified_time = max(os.path.getmtime(file_path), modified_time)
		
		# Reload all the files if the modified time is after the last time
		# it was modified
		if modified_time > last_modified_time:
			print "Reloading config files"
			file = open(files["tweets"], "r")
			for line in file.readlines():
				tweets.append(line)
			# Load in the list of corrections
			corrections = file_to_object(files["replacements"])
			# Reset the last load time
			last_modified_time = modified_time

		keys = corrections.keys()
		start_time = time.time()
		query = quote_join(keys, " OR ")
		results = api.GetSearch(term=query, per_page=1)
		if len(results) == 0:
			continue
		
		tweet = results[0]
		entry = find_correction(tweet.text, corrections)
		if not entry: # should never happen, but whatever
			continue
		
		text = entry["replace"]["text"]
		new_tweet = random.choice(tweets);
		new_tweet = new_tweet.replace(r"$USER", "@" + tweet.user.screen_name);
		new_tweet = new_tweet.replace(r"$ERROR", entry["find"]);
		new_tweet = new_tweet.replace(r"$CORRECTION", text);

		print new_tweet

		api.PostUpdate(status=new_tweet, in_reply_to_status_id=tweet.id)

		time_to_sleep = SECONDS_BETWEEN_TWEETS - (time.time() - start_time);
		time.sleep(time_to_sleep)
	except:
		print "Error: ", sys.exc_info()[0]
