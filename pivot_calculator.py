from file_processer import write_xlsx
from file_processer import read_json
from file_processer import write_json

from time import sleep
import time
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options



def get_html(url):
	options = Options()
	options.headless = True

	driver = webdriver.Firefox(executable_path="geckodriver.exe", options = options)

	driver.get(url)
	sleep(1)
	
	html = driver.page_source
	driver.close()
	return html


def get_table(url):
	html = get_html(url)
	soup = BeautifulSoup(html, 'lxml')

	table = soup.find('tbody',class_ = 'tv-data-table__tbody')

	table = table.find_all('tr')



	for i in range(len(table)):
		table[i] = table[i].find_all('td')
		for k in range(len(table[i])):
			table[i][k] = table[i][k]
		



	return table

def transform_table(table):
	new_table = []
	for row in table:
		new_table.append(row_to_dict(row))

	return new_table



def row_to_dict(row):
	dict_ = { 'name':None,
			  'last':None,
			  'min':None,
			  'max':None}

	
	dict_['name']= row[0].find('span',class_= 'tv-screener__description').text[0::]
	dict_['last']= float(row[1].text)
	dict_['min']= float(row[7].text)
	dict_['max']= float(row[6].text)
	return dict_

def compute_pivot(price):
	high = price['max']
	low = price['min']
	close = price['last']

	pivot = (high + low + close)/3

	r1 = 2*pivot - low
	r2 = pivot + (high-low)
	r3 = high + 2*(pivot -low)

	s1 = 2* pivot  - high
	s2 = pivot - (high -low)
	s3 = low - 2*(high -pivot)

	pivot = {"name":price['name'],
			 "pivot":pivot,
			 "r1":r1,
			 "r2":r2,
			 "r3":r3,
			 "s1":s1,
			 "s2":s2,
			 "s3":s3}

	return pivot

def write_pivot(table, name = "trading_view_"):
	configs = read_json('configs.json')
	file_name = configs[name+"last_workbook_name"]
	try:
		path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
		os.remove(path)
	except Exception:
		pass
	

	array = []
	for row in table:
		array.append(compute_pivot(row))

	now = time.strftime('%d-%m-%Y  %H-%M',time.localtime())
	file_name = name + "pivot, updated "+now+'.xlsx'

	
	configs[name+"last_workbook_name"]=file_name
	write_json('configs.json',configs)

	write_xlsx(file_name,array)



def execute():
	print("Парсинг..")
	table = transform_table(get_table('https://ru.tradingview.com/markets/currencies/rates-major/'))
	table += transform_table(get_table('https://ru.tradingview.com/markets/currencies/rates-exotic/'))
	table += transform_table(get_table('https://ru.tradingview.com/markets/currencies/rates-minor/'))
	write_pivot(table)
	print("Обновлено.")


def autorun():
	configs = read_json('configs.json')
	if configs['autorunned']==False:
		path = os.path.abspath(os.path.dirname(__file__))
		file_path = path+'\\pivot_calculator.exe'

		path = path.split("\\")[0:3:]

		s = ''
		for p in path:
			s+=p+'\\'

		s+='AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\pivot_calculator.bat'
		autorun_path = s

		bat = """@echo off
				 start '"""+file_path +"""'
			 	 pause
			 	 exit
	
			 	 """



		with open(autorun_path,'w') as f:
			f.write(bat)

		write_json('configs.json',{'autorunned':True})
		execute()




def main():
	autorun()
	while True:
		
		configs = read_json('configs.json')

		now_h = time.localtime()[3]
		now_m = time.localtime()[4]

		if now_h == configs['update_time_h'] and now_m == configs['update_time_m']:
			execute()
			print('done')
			sleep(60)

		sleep(30)



if __name__ == '__main__':
	main()





