#Imports
from bs4 import BeautifulSoup
import requests , re , random , os ,time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging

class Proxies:
	def __init__(self , data_file = 'json_data/data_header_details.json' , 
				pubproxy = 'http://pubproxy.com/api/proxy?port=8080,3128,3129,51200,8811,8089,33746,8880,32302,80,8118,8081',
				proxyscrape = 'https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=elite' ,
				free_p_l = 'https://free-proxy-list.net/'):

		self.data_file = data_file  # To save Location of where you have saved Json File
		self.data = json.load(open(os.path.abspath(self.data_file) , 'r'))
		self.pubproxy = pubproxy
		self.proxyscrape = proxyscrape
		self.free_p_l = free_p_l
		self.def_logger()

	# Definign Logger for this class
	def def_logger(self):
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)
		self.formatter = logging.Formatter('%(asctime)s : %(filename)s : %(funcName)s : %(levelname)s : %(message)s')
		self.file_handler = logging.FileHandler(os.path.abspath('log_data/proxies.log'))
		self.file_handler.setLevel(logging.DEBUG)
		self.file_handler.setFormatter(self.formatter)
		self.logger.addHandler(self.file_handler)
	
	# Function to return Header when called
	def return_header(self):
		header = {
				'user-agent':self.data['user_agents_scrap'][random.randint(0,len(self.data['user_agents_scrap'])-1)] , 
				'referer':self.data['referrer'][random.randint(0,len(self.data['referrer'])-1)],
				'Upgrade-Insecure-Requests': '0' , 
				'DNT':'1' , 
				'Connection':'keep-alive',
				'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Encoding':'gzip, deflate, br','Accept-Language':'en-US,en;q=0.5'
		}
		return header

	# Function to return Proxy from list of working Proxies
	def return_proxy(self):
		return self.data['working_proxies'][random.randint(0,len(self.data['working_proxies'])-1)]
	
	# Scrap User Agents from List provided in JSON file
	def scrap_user_agents(self):

		for link in self.data['user_agents_links']:
			try:
				site=requests.get(link)
				if site.status_code == requests.codes.ok:
					self.logger.info('Successfully got Link -> {}'.format(link))
					html_soup = BeautifulSoup(site.text , 'html.parser')
					response = html_soup.find_all('tr')
					for res in response[1:]:
						self.data['user_agents_scrap'].append(res.td.a.text)
				else:
					self.logger.debug('Status Code Mismatch -> {}'.format(link))
				time.sleep(random.randint(0,10))
			except Exception as E:
				self.logger.warning('Error Occured -> {} with Exception {}'.format(link,E))

	# Get proxies from Pubproxy
	def get_pubproxy(self , limit = 20):
		self.logger.info('Gettting Proxy from Pubproxy .. ')
		proxies = []
		for i in range(limit):
			try:
				proxy = requests.get(self.pubproxy).json()['data'][0]['ipPort']
				if proxy not in proxies:
					proxies.append(proxy)
			except Exception as E:
				self.logger.error('Something Went Wrong in Extracting from PubProxy .. ')
		self.logger.info('Called {} number of Proxies from PubProxy'.format(len(proxies)))
		return proxies

	# Get proxies from ProxyScrape
	def get_proxyscrape(self):
		try:
			response = requests.get(self.proxyscrape)
			if response.status_code == requests.codes.ok:
				proxies = response.text.split('\r\n')
				self.logger.info('Called {} number of Proxies from ProxyScrape'.format(len(proxies)))
				return proxies
			else:
				self.logger.error('Status Code Mismatch From ProxyScrape .. ')
				return '0'
		except Exception as E:
			self.logger.error('Something went Wrong in Extracting from ProxyScape .. -> {}'.format(E))
			return '0'

	# Get proxies from Free Proxy List
	def get_free_p_l(self):
			try:
				print('Requesting Proxy Site...')
				response = requests.get(self.free_p_l)
				print('Get Proxy Site...')
				if response.status_code==requests.codes.ok:
					page_soup = BeautifulSoup(response.text, "html.parser")
					textarea = page_soup.find('textarea').text
					proxies = re.findall('\d+\.\d+\.\d+\.\d+\:\d+',textarea)
					self.logger.info('Called {} number of Proxies from free-proxy-list ..'.format(len(proxies)))
					return proxies
				else:
					self.logger.error('Status Code Mismatch From free-proxy-list .. ')
					return '0'
			except Exception as E:
				self.logger.error('Something went Wrong in Extracting from free-proxy-list .. -> {}'.format(E))
				return '0'

	# To filter Duplicated Proxies
	def get_proxies(self):
		self.data['proxies'] = self.get_free_p_l()
		self.data['proxies'] = list(filter(None , self.data['proxies']))

	# To save json data in disk
	def save_data(self):
		with open(self.data_file, 'w') as outfile:
			json.dump(self.data, outfile, indent=4)

class Proxy_Checker(Proxies):
	def __init__(self):
		Proxies.__init__(self)
		self.check_url = 'https://www.azlyrics.com/'

	def fetch(self, proxies):
		try:
			with requests.get(self.check_url , proxies = {'http':proxies,'https':proxies} ,timeout = 10) as response:
				if response.status_code == requests.codes.ok:
					self.logger.info('SuccessFul Proxy-> {}'.format(proxies))
					return proxies
				else:
					self.logger.warning('Status Code {} Mismatch Proxy-> {}'.format(response.status_code,proxies))
					return '0'
		except Exception as E:
			self.logger.warning('Timeout Proxy-> {}'.format(proxies))
			return '0'

	async def check_proxies(self):
		proxies = self.data['proxies']
		self.data['working_proxies'] = []

		with ThreadPoolExecutor(max_workers = 50) as executor:
			loop = asyncio.get_event_loop()
			tasks = [
					loop.run_in_executor(executor , self.fetch , pro)
					for pro in proxies
					]
			for response in await asyncio.gather(*tasks):
				if response != '0':
					self.data['working_proxies'].append(response)
	
	def async_get_proxies(self):
		try:	
			self.loop = asyncio.get_event_loop()
			self.loop.set_debug(1)
			future = asyncio.ensure_future(self.check_proxies())
			self.loop.run_until_complete(future)
		except Exception as E:
			self.logger.warning(E)
		finally:
			self.loop.close()

if __name__ == "__main__":
	pro = Proxy_Checker()
	pro.get_proxies()
	pro.async_get_proxies()
	pro.save_data()