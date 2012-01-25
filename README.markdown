# Grammar Nazi Twitter Bot #

## Setup ##

### Dependencies ###
External modules needed are twitter and json. Install them using

	easy_install python-twitter
	easy_install json

### Credentials ###
Open up the credentials.json file and place your app's consumer key and consumer secret
as well as the user's access token and access secret.

### Dictionary ###
Open replacements.json and follow the template to insert new replacements. As of now
you can insert either a grammatical error or a spelling error.

### Tweets ###
Modify tweets.dat to change the contents of the tweets.  $USER, $CORRECTION, and $ERROR
will be changed to the appropriate values for each tweet. Tweets are delimited by a new
line, and tweets will be chosen at random among the list.

## Run Grammar Bot ##
	python grammar-bot.py


### Brought to you by ###
Rishi Ishairzay and Kyle Morgan
