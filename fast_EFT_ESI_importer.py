#!/usr/bin/env python3

import requests
import json
import webbrowser
import base64

#---------------------------
#Define functions
#---------------------------

def check_error(esi_response, job):
	status_code = esi_response.status_code
	
	if status_code != 200:
		#Error
		print('Failed to '+job+'. Error',esi_response.status_code,'-', esi_response.json()['error'])
		error = True
		global has_errors
		has_errors = True
	else:
		error = False
		try:
			#Try to print warning
			print('Warning',esi_response.headers['warning'])
		except KeyError:
			warning = False
	
	return error
	
	
#Code for logging in
def logging_in():
	login_url = 'https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri=http://localhost/oauth-callback&client_id='+client_id+'&scope=esi-skills.read_skills.v1+esi-clones.read_implants.v1'

	webbrowser.open(login_url, new=0, autoraise=True)

	authentication_code = input("Give your authentication code: ")
	
	combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
	authentication_url = "https://login.eveonline.com/oauth/token"
	
	esi_response = requests.post(authentication_url, headers =  {"Authorization":"Basic "+combo}, data = {"grant_type": "authorization_code", "code": authentication_code} )
	
	if not check_error(esi_response, 'exchange authorization code for tokens'):
		response = esi_response.json()
		
		access_token = response['access_token']
		refresh_token = response['refresh_token']
		
		character_info = get_char_info(access_token)
		
		#Check if character info errored
		if character_info == 'error':
			return
			
		character_info["refresh_token"] = refresh_token

		config['characters'].append(character_info)
		
		print('Character: '+character_info['character_name']+' logged in')
		
		#Save new config
		with open('config.txt', 'w') as outfile:
			json.dump(config, outfile, indent=4)
	else:
		return
	
	return config
	
#Use refresh token to get new access token
def refresh_auth(refresh_token):
	refresh_url = 'https://login.eveonline.com/oauth/token'
	
	combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
	esi_response = requests.post(refresh_url, headers =  {"Authorization":"Basic "+combo}, data = {"grant_type": "refresh_token", "refresh_token": refresh_token} )
	
	if not check_error(esi_response, 'refresh access token'):
		access_token = esi_response.json()['access_token']
	else:
		return 'error'

	return access_token
	
#Get info on the character by using the access token
def get_char_info(access_token):
	
	url = 'https://login.eveonline.com/oauth/verify'
	esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
	
	if not check_error(esi_response, 'get character info with access token'):
		response = esi_response.json()
		character_id = response['CharacterID']
		character_name = response['CharacterName']
		character_info = {"character_id":character_id, "character_name":character_name}
	else:
		return 'error'

	return character_info

def main_menu():
	#List saved characters
	if len(config['characters']) == 0:
		print('\nNo characters saved')
	else:
		print('\nSaved characters:')
		for n in range(0, len(config['characters'])):
			print(n, config['characters'][n]['character_name'])
			
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
		for n in range(0, len(config['characters'])):
			print(n, config['characters'][n]['character_name'])
			
		user_input = input("Character number: ")
		
		try:
			user_input = int(user_input)
			
			if user_input <= len(config['characters']):
				del config['characters'][user_input]
				#Save new config
				with open('config.txt', 'w') as outfile:
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
			item_id = json.load(open('item_id.txt'))
		except (IOError, json.decoder.JSONDecodeError):
			#Some error. Just start the id list from scratch
			item_id = {}
			with open('item_id.txt', 'w') as outfile:
				json.dump(item_id, outfile, indent=4)
		
		#Improt characters one by one
		for n in range(0, len(config['characters'])):
			
			character_name = config['characters'][n]['character_name']
			character_id = config['characters'][n]['character_id']
			refresh_token = config['characters'][n]['refresh_token']
			
			print('importing '+character_name+'...')
			
			access_token = refresh_auth(refresh_token)
			
			#Check if the access token didn't error
			if access_token == 'error':
				return
			
			#Import skills and put them in the string
			#import implants and put them to same string
			#Write the string to file and be done
			
			output = ''
			
			#Import skills first
			url = 'https://esi.tech.ccp.is/v4/characters/'+str(character_id)+'/skills/?datasource=tranquility'
			
			esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
			if not check_error(esi_response, 'get character skills'):
				skills = esi_response.json()['skills']
				
				for n in range(0, len(skills)):
					skill_id = skills[n]['skill_id']
					skill_level = skills[n]['active_skill_level']
					
					#Get item name from the saved list
					try:
						skill_name = item_id[str(skill_id)]
					except KeyError:
						#Unknown skill. Get name from API
						print('Fetching skill name for ID', skill_id,'-', end="")
						url = "https://esi.tech.ccp.is/v3/universe/types/"+str(skill_id)+"/"
						esi_response = requests.get(url)
						if esi_response.status_code == 200:
							skill_name = esi_response.json()['name']
							print(' ',skill_name)
							item_id[skill_id] = skill_name
						else:
							print(esi_response.status_code,'-', esi_response.json()['error'], '- skill ID: '+skill_id)
							
					output = output + skill_name + '=' + str(skill_level) + '\n'
			else:
				return
				
			url = 'https://esi.tech.ccp.is/v1/characters/'+str(character_id)+'/implants/?datasource=tranquility'
			esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
			
			if not check_error(esi_response, 'get character implants'):
				implants = esi_response.json()
				
				for n in range(0, len(implants)):
					implant_id = implants[n]
					
					try:
						implant_name = item_id[str(implant_id)]
					except KeyError:
						print('Fetching implant name for ID', implant_id,'-', end="")
						url = "https://esi.tech.ccp.is/v3/universe/types/"+str(implant_id)+"/"
						esi_response = requests.get(url)
						if esi_response.status_code == 200:
							implant_name = esi_response.json()['name']
							print(' ', implant_name)
							item_id[implant_id] = implant_name
						else:
							print(esi_response.status_code,'-', esi_response.json()['error'], '- implant ID: '+implant_id)
				
					output = output + 'Implant=' + implant_name + '\n'
			else:
				return
				
			#save item id names
			with open("item_id.txt", "w") as outfile:
				json.dump(item_id, outfile, indent=4)
					
			#Write skills to txt
			filename = character_name+'.chr'
			with open(filename, "w") as text_file:
				print(output, file=text_file)
				
			
		#stop running after imported
		global run
		run = False
	
	
	return
	
def reset():
	item_id = {}
	with open('item_id.txt', 'w') as outfile:
		json.dump(item_id, outfile, indent=4)
		
	config = {"client_id":'', "client_secret":'', "characters":[]}
	with open('config.txt', 'w') as outfile:
		json.dump(config, outfile, indent=4)
	
	#Resets configuration
	print('\nno client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
	client_id = input("Give your client ID: ")
	client_secret = input("Give your client secret: ")
	config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
	with open('config.txt', 'w') as outfile:
			json.dump(config, outfile, indent=4)
	item_id = {}
	with open('item_id.txt', 'w') as outfile:
		json.dump(item_id, outfile, indent=4)
	
	
#---------------------------
#Start the actual script now
#---------------------------

print('\nESI API importer for EFT by Hirmuolio Pine')

#Check if client ID and client secret are in the onfiguration file.
#If not ask for them and write them to the file.
try:
	config = json.load(open('config.txt'))
	
	try:
		client_id = config['client_id']
		client_secret = config['client_secret']
	except KeyError:
		print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
		client_id = input("Give your client ID: ")
		client_secret = input("Give your client secret: ")
		config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
		with open('config.txt', 'w') as outfile:
			json.dump(config, outfile, indent=4)
		
except (IOError, json.decoder.JSONDecodeError):
	print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
	client_id = input("Give your client ID: ")
	client_secret = input("Give your client secret: ")
	config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
	with open('config.txt', 'w') as outfile:
		json.dump(config, outfile, indent=4)


import_characters()

print('Imprt completed')
if has_errors == True:
	input("There were errors. Press enter to exit...")
