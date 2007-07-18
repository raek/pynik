import re
import urllib2
import utility
from commands import Command

def google_pages(string):
	url = 'http://www.google.se/search?q=' + utility.UtilityPlugin.instance.escape(string) + '&ie=UTF-8&oe=UTF-8'

	request = urllib2.Request(url)
	request.add_header('User-Agent', 'PynikOpenAnything/1.0 +')

	opener = urllib2.build_opener()
	data = opener.open(request).read()

	search = re.search('swrnum=(.*?)>', data)

	if search:
		result = search.group(1)

		if result:
			return int(result)
		else:
			return None
	else:
		return None

def google_divisor(int1, int2):
	if int1 < int2:
		biggest = int1
	else:
		biggest = int2

	if biggest > 1000000:
		divisor = 1000000.0
		unit = 'm'
	elif biggest > 1000:
		divisor = 1000.0
		unit = 'k'
	else:
		divisor = 1
		unit = ''
	return (divisor, unit) 


					
class Googlefight(Command):
	def __init__(self):
		pass
	
	def trig_googlefight(self, bot, source, target, trigger, argument):
		args = argument.split('|', 2)
		if len(args) == 2 and len(args[0]) > 0 and len(args[1]) > 0:
			result1 = google_pages(args[0])
			result2 = google_pages(args[1])
			if result1 and result2:
				grej = google_divisor(result1, result2)

				result1 = result1 / grej[0]
				result2 = result2 / grej[0]
				unit = grej[1]

				if result1 == result2:
					bot.tell(target, "It's a tie! " + str(result1/1000.0) + "k hits!")
				elif result1 > result2:
					bot.tell(target, args[0] + ' is the winner! (' + str(result1) + unit + ' to ' + str(result2) + unit + ')')
				else:
					bot.tell(target, args[1] + ' is the winner! (' + str(result2) + unit + ' to ' + str(result1) + unit + ')')
			else:
				bot.tell(target, "Couldn't search.")
		else:
			bot.tell(target, "Usage: .googlefight arg1|arg2")