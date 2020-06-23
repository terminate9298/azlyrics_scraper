#Imports

from bs4 import BeautifulSoup
import requests , re , random , os ,time,sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from bin.proxies import *

class AZLyrics(Proxy_Checker):
	def __init__(self):
		Proxy_Checker.__init__(self)
		self.base_url = 'https://www.azlyrics.com/'
		self.url_max_retrires = 5
		self.max_retries = 5
		self.max_workers = 100
		self.timeout = 10
		self.az_link_data = 'json_data/data_to_scrap.json'
		self.az_link_lyrics = 'json_data/data_lyrics.json'
		self.az_load_data()
		self.az_logger()

	def az_load_data(self):
		self.az_data = json.load(open(os.path.abspath(self.az_link_data) , 'r'))
		self.az_lyrics = json.load(open(os.path.abspath(self.az_link_lyrics) , 'r'))

	def az_logger(self):
		self.az_logger = logging.getLogger(__name__)
		self.az_logger.setLevel(logging.DEBUG)
		self.az_formatter = logging.Formatter('%(asctime)s : %(filename)s : %(funcName)s : %(levelname)s : %(message)s')
		self.az_file_handler = logging.FileHandler(os.path.abspath('log_data/main.log'))
		self.az_file_handler.setLevel(logging.DEBUG)
		self.az_file_handler.setFormatter(self.az_formatter)
		self.az_logger.addHandler(self.az_file_handler)

	def save_az_data(self):
		with open(self.az_link_data, 'w') as outfile:
			json.dump(self.az_data, outfile, indent=4)

	def save_az_lyrics(self):
		with open(self.az_link_lyrics , 'w') as outfile:
			json.dump(self.az_lyrics , outfile, indent=4)

	def get_url(self , url):
		flag = self.url_max_retrires
		while(flag):
			header = self.return_header()
			proxy = self.return_proxy()
			try:
				site = requests.get(url , headers = header , proxies = {'http':proxy,'https':proxy},timeout = self.timeout)
				if site.status_code == requests.codes.ok:
					html_soup = BeautifulSoup(site.text , 'html.parser')
					if len(html_soup.find_all('div',class_ = 'alert alert-info')) == 0:
						self.az_logger.info('SuccessFul Get Request -> {} using Proxy -> {} on try-> {}'.format(url,proxy,flag))
						flag=0
						return html_soup
					else:
						self.az_logger.debug('Recapta Detected -> {} using Proxy -> {} on try-> {}'.format(url , proxy , flag))
						flag -= 1
						if flag == 0:
							return '0'
				else:
					self.az_logger.debug('Proxy Status Mismatch -> {} using Proxy -> {} on Try -> {}'.format(site.status_code , proxy , flag))
					flag -= 1
					if flag ==0:
						return '0'
			except Exception as E:
				self.az_logger.debug('Something Went Wrong -> {} using  Proxy -> {} Error -> {} on try-> {}'.format(url,proxy,E,flag))
				flag -= 1
				if flag == 0:
					return '0'
		return '0'

	def az_songs_by_list(self , mode = 'Existing'):
		if mode == 'New':
			self.az_data['scrap_singer_success'] = []
			self.az_data['simple_urls'] = []
			self.az_data['songs_details'] = []
			self.az_data['albums_details'] = []
			flag = 0
		if mode == 'Existing':
			flag = self.az_data['flag']
		temp_flag = self.max_retries
		while(temp_flag):
			for url in self.az_data['scrap_by_singer']:
				if url not in self.az_data['scrap_singer_success']:
					try:
						html_soup = self.get_url(url)
						if html_soup != '0':
							title = html_soup.find('h1').text
							songs = html_soup.find_all('div',class_ = 'listalbum-item')
							albums = html_soup.find_all('div', class_ = 'album')
							for album in albums:
								album_id = album.get('id')
								album_name = album.b.text.replace('"','')
								album_type = album.text.split(':')[0]
								if re.search("\(([\d+]+)\)",album.text) is not None:
									album_year = re.findall("\(([\d+]+)\)",album.text)[0]
								else:
									album_year = 'Not Defined'
								self.az_data['albums_details'].append({'id': album_id,'singer_name':title,'name':album_name,'type':album_type,'year':album_year})
							for song in songs:
							    song_href = song.a.get('href')
							    song_name = song.a.text
							    flag += 1
							    self.az_data['songs_details'].append({'song_id':flag ,'singer_name':title ,'song_name': song_name,'song_href': song_href})
							    self.az_data['simple_urls'].append(song_href)
							self.az_data['scrap_singer_success'].append(url)
							self.az_logger.info('SuccessFully Parsed the Request -> {}'.format(url))
						else:
							self.az_logger.debug('UnSuccessFul to Parse the Request -> {} ..!! Max Retries'.format(url))
							# data['scrap_singer_unsuccess'].append(url)
					except Exception as E:
						self.az_logger.warning('Something Wrong while Requesting -> {} Error -> {} on line No. -> {}'.format(url,E,sys.exc_info()[-1].tb_lineno))
			temp_flag -= 1
		self.az_data['flag'] = flag
		self.save_az_data()

	def add_urls(self , urls = []):
		for url in urls:
			if url not in self.az_data['scrap_by_singer']:
				self.az_data['scrap_by_singer'].append(url)
		self.save_az_data()

	def lyrics_from_link(self , link):
		if '../' in link:
			temp_link = self.base_url + link.split('../')[1]
		else:
			temp_link = link
		html_soup = self.get_url(temp_link)
		if html_soup != '0':
			try:
				singer = html_soup.find('div' , class_ = 'lyricsh').h2.text
				song_name = html_soup.find('div' , class_ = 'col-xs-12 col-lg-8 text-center').find_all('div',class_= 'div-share')[1].text.split('"')[1]
				lyrics = html_soup.find('div' , class_ = 'col-xs-12 col-lg-8 text-center').find_all('div')[5].text
				return {'link':link, 'artist':singer , 'song_name':song_name ,'lyrics': lyrics}
			except Exception as E:
				self.az_logger.warning('Error in Scrapping lyrics {} Lineno.->{}'.format(E , sys.exc_info()[-1].tb_lineno))
				return '0'
		else:
			return '0'
			
	async def get_batch_lyrics(self):
		unsuccess = []
		for list_batch in self.az_data['simple_urls']:
			if list_batch not in self.az_lyrics['completed']:
				unsuccess.append(list_batch)
		self.az_logger.info('UnSuccessFul links {}'.format(unsuccess[0]))
		flag = self.max_retries
		while(flag):
			try:
				with ThreadPoolExecutor(max_workers = self.max_workers) as executor:
					loop = asyncio.get_event_loop()
					tasks = [
							loop.run_in_executor(executor , self.lyrics_from_link , pro)
							for pro in unsuccess
					]
					for response in await asyncio.gather(*tasks):
						if response != '0':
							self.az_lyrics['lyrics'].append(response)
							self.az_lyrics['completed'].append(response['link'])
							unsuccess.remove(response['link'])
					if len(unsuccess) == 0:
						flag = 0
					else:
						flag -= 1
			except Exception as E:
				self.az_logger.warning('Scrapping Went Wrong -> {} Lineno. -> {}'.format(E , sys.exc_info()[-1].tb_lineno))
			finally:
				self.save_az_lyrics()
		self.az_logger.info('Scrapped Successful... No. of Lyrics in file is  {}'.format(len(self.az_lyrics['completed'])))
		self.save_az_lyrics()

	def start_scrapping(self):
		try:
			self.loop = asyncio.get_event_loop()
			self.loop.set_debug(1)
			future = asyncio.ensure_future(self.get_batch_lyrics())
			self.loop.run_until_complete(future)
		except Exception as E:
			self.az_logger.warning('Warning Log -> {} Lineno -> {}'.format(E, sys.exc_info()[-1].tb_lineno))
		finally:
			self.loop.close()

if __name__ == "__main__":
	pass

