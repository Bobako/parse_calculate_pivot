from file_processer import read_json
from file_processer import write_json
from time import sleep

def main():
	configs = read_json('configs.json')
	h = str(configs['update_time_h'])
	m = str(configs['update_time_m'])

	if len(h)==1:
		h = '0'+h

	if len(m)==1:
		m = '0'+m	

	old = h+':'+m

	print('Автообновление таблицы установлено на',old)

	new = input('Изменить на:')

	h,m = map(int,new.split(':'))

	configs['update_time_h'] = h
	configs['update_time_m'] = m
	write_json('configs.json',configs)

	old = str(h)+':'+str(m)

	print('Изменено на',old)

	sleep(3)

if __name__ == '__main__':
	main()