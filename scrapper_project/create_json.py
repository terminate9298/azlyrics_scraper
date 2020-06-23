import json

def save_json(data , file_link = 'data.json'):
    with open(file_link, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def creating_header():
	# data = json.load(open('data_header_details.json', 'r'))
	data = {}
	data['user_agents_links'] = [
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/',
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/2',
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/linux/',
	'https://developers.whatismybrowser.com/useragents/explore/software_name/safari/',
	'https://developers.whatismybrowser.com/useragents/explore/software_name/opera/',
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/chrome-os/',
	'https://developers.whatismybrowser.com/useragents/explore/hardware_type_specific/mobile/',
	'https://developers.whatismybrowser.com/useragents/explore/operating_platform_string/redmi/',
	'https://developers.whatismybrowser.com/useragents/explore/software_name/instagram/',
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/android/',
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/ios/',
	'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/mac-os-x/'
	]
	data['referrer'] = [
        "https://duckduckgo.com/",
        "https://www.google.com/",
        "http://www.bing.com/",
        "https://in.yahoo.com/",
        "https://www.azlyrics.com/",
        "https://www.dogpile.com/",
        "http://www.yippy.com",
        "https://yandex.com/"
        ]
        
	data['user_agents_scrap'] = []
	data['proxies'] = []
	data['working_proxies'] = []
	save_json(data,'json_data/data_header_details.json')

def creating_lyrics():
	data = {}
	data['lyrics'] = []
	data['completed'] = []
	save_json(data , 'json_data/data_lyrics.json')
def creating_to_scrap():
	data = {}
	data['scrap_by_singer'] = []
	data['simple_urls'] = []
	data['scrap_singer_success'] = []
	data['songs_details'] = []
	data['albums_details'] = []
	data['flag'] = 0
	save_json(data , 'json_data/data_to_scrap.json')


if __name__ == "__main__":
	creating_lyrics()
	creating_header()
	creating_to_scrap()