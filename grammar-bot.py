import json, pycurl

# Load in the credentials config file into credentials dictionary
config_file = open("credentials.json", "r")
config = ""
for line in config_file: config += line
credentials = json.loads(config)

