import json
import time
import telegram
import ffmpy
import os
from telegram.error import NetworkError, Unauthorized
from random import randint
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve

YLYL_ENDPOINT = 'https://a.4cdn.org/wsg/{}.json'
visited_threads = []
waiting_posts = []
bot = telegram.Bot('333255572:AAEPfnc1n4qWqqXDt_JClvKzbD656nyV-6c')	
CHAN_ID = -1001100456325
try:
    update_id = bot.getUpdates()[0].update_id
except IndexError:
    update_id = None

def send_message(text):
	bot.send_message(CHAN_ID, text)

def send_document(doc):
	bot.send_document(CHAN_ID, doc)

def dump_threads():
	global visited_threads
	with open('threads.txt', 'a+') as f:
		for thread in waiting_posts:
			f.write(str('{}\n'.format(thread)))
	print('Wrote {} files...'.format(len(visited_threads)))
	visited_threads = []

def already_posted():
	with open('threads.txt') as f:
		return f.read().splitlines()

def get_webms(boards):
	for x in range(1, boards + 1):
		print('board {}'.format(x))
		r = urlopen(YLYL_ENDPOINT.format(x)).read()
		struct = json.loads(r)
		for post in struct["threads"]:
			op = post["posts"][0]
			if 'com' in op:
				for resp in post["posts"]:
					if 'filename' in resp:
						if not 'sticky' in resp and resp['ext'] == '.webm':
							if not resp['tim'] in waiting_posts and not resp['tim'] in visited_threads:
								waiting_posts.append(resp['tim'])
			elif 'sub' in op:
				for resp in post["posts"]:
					if 'filename' in resp:
						if not 'sticky' in resp and resp['ext'] == '.webm':
							if not resp['tim'] in waiting_posts and not resp['tim'] in visited_threads:
								waiting_posts.append(resp['tim'])

def post_new_webm():
	if len(waiting_posts) > 0:
		while len(waiting_posts) > 0:
			post = waiting_posts[0]
			del waiting_posts[0]
			download_file(post)
			ff = ffmpy.FFmpeg(
				inputs={'files/{}.webm'.format(post) : None},
				outputs={'files/{}.mp4'.format(post) : None}
			)
			ff.run()
			os.remove('files/{}.webm'.format(post))
			send_document(open('files/{}.mp4'.format(post), 'rb'))
			os.remove('files/{}.mp4'.format(post))
			visited_threads.append(post)

def clean_file():
	open('threads.txt', 'w').close()

def download_file(id):
	urlretrieve('http://i.4cdn.org/wsg/{}.webm'.format(id), 'files/{}.webm'.format(id))

def test():
	global visited_threads
	visited_threads.append(randint(100, 2000))
	print('{}'.format(visited_threads))

sched = BackgroundScheduler()
sched.start()
sched.add_job(clean_file, 'interval', seconds = 15 * 60)
sched.add_job(lambda: get_webms(10), 'interval', seconds = 18 * 60)
sched.add_job(post_new_webm, 'interval', seconds = 2 * 60)
sched.add_job(dump_threads, 'interval', seconds = 6 * 60)

print("Waiting to exit; press <CTRL-C> to quit.")
while True:
	time.sleep(1)