#!/usr/bin/env python3

import json

import EFT_ESI_code

#---------------------------
#Define functions
#---------------------------

	

def main_menu():
	#List saved characters
	if len(config['characters']) == 0:
		print('\nNo characters saved')
	else:
		print('\nSaved characters:')
		for name in config['characters']:
			print(name)
			
	print('\n[S] Start importing\n[D] Delete characters\n[L] Log in a character\n[R] Reset')
	user_input = input("[S/D/L/R] ")

	if user_input == 'S' or user_input == 's':
		EFT_ESI_code.import_characters()
	elif user_input == 'D' or user_input == 'd':
		EFT_ESI_code.delete_characters()
		main_menu()
	elif user_input == 'L' or user_input == 'l':
		print('Log in a new character.')
		EFT_ESI_code.logging_in()
		main_menu()
	elif user_input == 'R' or user_input == 'r':
		EFT_ESI_code.reset()
		main_menu()
	else:
		main_menu()

		
try:
	config = json.load(open('config.json'))
	
	try:
		client_id = config['client_id']
		client_secret = config['client_secret']
	except KeyError:
		print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
		client_id = input("Give your client ID: ")
		client_secret = input("Give your client secret: ")
		config = {"client_id":client_id, "client_secret":client_secret, "characters":{} }
		with open('config.json', 'w') as outfile:
			json.dump(config, outfile, indent=4)
except (IOError, json.decoder.JSONDecodeError):
	print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
	client_id = input("Give your client ID: ")
	client_secret = input("Give your client secret: ")
	config = {"client_id":client_id, "client_secret":client_secret, "characters":{} }
	with open('config.json', 'w') as outfile:
		json.dump(config, outfile, indent=4)

		
main_menu()

print('\nImport completed')
