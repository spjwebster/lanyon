import re

def slugify(string):
	if not hasattr(slugify, ''):
		slugify.regex = re.compile(r'[^a-z0-9]+')
	return re.sub(slugify.regex, '-', string.lower())