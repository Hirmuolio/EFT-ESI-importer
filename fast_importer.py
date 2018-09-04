#!/usr/bin/env python3

import json

import esi_calling

#---------------------------
#Define functions
#---------------------------



def logging_in():
	#Log in character and save its info
	scopes = 'esi-skills.read_skills.v1+esi-clones.read_implants.v1'
	client_id = config['client_id']
	client_secret = config['client_secret']
	
	tokens = esi_calling.logging_in(scopes, client_id, client_secret)
	token_info = esi_calling.get_token_info(tokens)
	
	
	config['characters'][token_info['character_name']] = {}
	config['characters'][token_info['character_name']]['tokens'] = tokens
	config['characters'][token_info['character_name']]['character_id'] = token_info['character_id']
	
	with open('config.json', 'w') as outfile:
		json.dump(config, outfile, indent=4)
	
	print('Character: '+ token_info['character_name'] +' logged in and saved')
	
	return config
	

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
		import_characters()
	elif user_input == 'D' or user_input == 'd':
		delete_characters()
	elif user_input == 'L' or user_input == 'l':
		print('Log in a new character.')
		logging_in()
	elif user_input == 'R' or user_input == 'r':
		reset()
	else:
		print('[R]un inporting\n[E]dit characters\n[L]og in a character')
	return

def delete_characters():
	#Edit characters and return to main menu
	if len(config['characters']) == 0:
		print('No characters to delete')
	else:
		print('\nSelect the character to delete')
		n = 0
		name_id = {}
		for name in config['characters']:
			print('['+str(n)+']', name)
			name_id[str(n)] = name
			n = n+1
			
		user_input = input("Character number: ")
		
		try:
			user_input = int(user_input)
			
			if user_input <= len(name_id):
				del config['characters'][name_id[str(user_input)]]
				#Save new config
				with open('config.json', 'w') as outfile:
					json.dump(config, outfile, indent=4)
			else:
				print('No character', user_input)
		except ValueError:
			print('invalid input', user_input)
		
	return
	
def import_characters():
	
	if len(config['characters']) == 0:
		print('No characters to import')
	else:
		print('importing characters')
		#Load saved skill names and implant names
		try:
			item_id = json.load(open('item_id.json'))
		except (IOError, json.decoder.JSONDecodeError):
			#Some error. Just start the id list from scratch
			item_id = {}
			with open('item_id.json', 'w') as outfile:
				json.dump(item_id, outfile, indent=4)
		
		#Improt characters one by one
		for name in config['characters']:
			
			tokens = config['characters'][name]['tokens']
	
			tokens = esi_calling.check_tokens(tokens, client_id = config['client_id'], client_secret = config['client_secret'])
			
			character_id = config['characters'][name]['character_id']
			
			print('\nimporting '+name+'...')

			
			#Import skills and put them in the string
			#import implants and put them to same string
			#Write the string to file and be done
			
			output = ''
			
			#Import skills first			
			esi_response = esi_calling.call_esi(scope = '/v4/characters/{par}/skills', url_parameter=character_id, tokens = tokens, calltype='get', job = 'import character skills')


			skills = esi_response.json()['skills']
			
			for n in range(0, len(skills)):
				skill_id = skills[n]['skill_id']
				skill_level = skills[n]['active_skill_level']
				
				#Get item name from the saved list
				try:
					skill_name = item_id[str(skill_id)]
				except KeyError:
					#Unknown skill. Get name from API

					#print('                \r', end="")#clears the line to stop things from previous loop from staying
					print(str(n+1)+'/'+str(len(skills)+1) + ' Fetching skill name for ID:', skill_id, end="")
					esi_response = esi_calling.call_esi(scope = '/v3/universe/types/{par}', url_parameter=skill_id, tokens = tokens, calltype='get', job = 'get implant name')
					
					skill_name = esi_response.json()['name']
					print(' ', skill_name)
					item_id[skill_id] = skill_name
						
				output = output + skill_name + '=' + str(skill_level) + '\n'
			print('')
			esi_response = esi_calling.call_esi(scope = '/v1/characters/{par}/implants', url_parameter=character_id, tokens = tokens, calltype='get', job = 'import character implants')
			
			implants = esi_response.json()
			
			for implant_id in implants:
				
				try:
					implant_name = item_id[str(implant_id)]
				except KeyError:
					print('                                             \r', end="")#clears the line to stop things from previous loop from staying
					print('\rFetching implant name for ID:', implant_id, end="")
					esi_response = esi_calling.call_esi(scope = '/v3/universe/types/{par}', url_parameter=implant_id, tokens = tokens, calltype='get', job = 'get implant name')
		
					implant_name = esi_response.json()['name']
					print(' ', implant_name, end="")
					item_id[implant_id] = implant_name
			
				output = output + 'Implant=' + implant_name + '\n'
			print('')

			#save item id names
			with open("item_id.json", "w") as outfile:
				json.dump(item_id, outfile, indent=4)
					
			#Write skills to txt
			filename = name+'.chr'
			with open(filename, "w") as text_file:
				print(output, file=text_file)
				
			
		#stop running after imported
		global run
		run = False
	
	
	return
	
def reset():
	item_id = {}
	with open('item_id.json', 'w') as outfile:
		json.dump(item_id, outfile, indent=4)
		
	config = {"client_id":'', "client_secret":'', "characters":[]}
	with open('config.json', 'w') as outfile:
		json.dump(config, outfile, indent=4)
	
	#Resets configuration
	print('\nno client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
	client_id = input("Give your client ID: ")
	client_secret = input("Give your client secret: ")
	config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
	with open('config.json', 'w') as outfile:
			json.dump(config, outfile, indent=4)
	item_id = {}
	with open('item_id.json', 'w') as outfile:
		json.dump(item_id, outfile, indent=4)
	
	
#---------------------------
#Start the actual script now
#---------------------------

print('\nESI API importer for EFT by Hirmuolio Pine')

#Check if client ID and client secret are in the onfiguration file.
#If not ask for them and write them to the file.
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

import_characters()

print('\nImport completed')
