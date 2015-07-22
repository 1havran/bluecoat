import mechanize
import cookielib
import getpass
import sys

categories = [["error", []], ["none", []]]
browser = mechanize.Browser()
browser.set_handle_robots(False)
cookie_jar = cookielib.LWPCookieJar()
browser.set_cookiejar(cookie_jar)

default_url = "https://192.168.1.1:8082/ContentFilter/TestUrl/"
default_user = "admin"

print
print "URL Categorization from Bluecoat ProxySG"
print "-"*60

if len(sys.argv) < 2:
	print "Not enough arguments!"
	print "Missing file with URL to categorize!"
	print "Usage: "+ sys.argv[0] + " <file_with_urls_split_by_newline>"
	exit()

host = raw_input("Enter URL [default: " + default_url + "]: ")
if not host:
	host = default_url

user = raw_input("Enter username [default: " + default_user + "]: ")
if not user:
	user = default_user
	
password = getpass.getpass("Password: ")

output_file = raw_input("Enter output file [default: workfile.txt]: ")
if not output_file:
	output_file = 'workfile.txt'


def categorize(url):
	browser.add_password(host + url, user, password)
	try:
		response = browser.open(host + url)
		res = response.read()
				
		counter = 0
		for line in res.split("\n"):
			for category in line.split("; "):
				if category != 'none' and category != '':
					counter += 1
					
				categoryExist = False
				for item in categories:	
					if item[0] != 'none':
						if item[0] == category:
							categoryExist = True
							if url not in item[1]:
								item[1].append(url)
							
				if category != 'none' and not categoryExist:
					categories.append([category, [url]])
		
		if counter < 1:
			categories[1][1].append(url)
			
	except (mechanize.HTTPError,mechanize.URLError) as e:
		if isinstance(e,mechanize.HTTPError):
			categories[0][1].append(url)


def bluecoat():
	try:
		num_lines = sum (1 for line in open(sys.argv[1]))

		f = open(sys.argv[1], 'r')
		count = 0
		for line in f:
			count += 1
			line = line.strip()
			print str(count) + "/" + str(num_lines),
			print line
			categorize(line)
		f.close()

		print ""
		categories.sort()
		ff = open(output_file, 'w')
		for item in categories:
			if item[0] != '':
				item[1].sort()
				ff.write(str(item) + "\n")
				print item
		ff.close()
		
	except IOError as e:
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
	except:
		print "Error occured:", sys.exc_info()[0]
		raise
	
bluecoat()

