#!/usr/bin/env python3

import requests
import json
import webbrowser
import base64

has_errors = False
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
	login_url = 'https://login.eveonline.com/oauth/authorize?response_type=token&redirect_uri=http://localhost/oauth-callback&client_id='+client_id+'&scope=esi-skills.read_skills.v1+esi-clones.read_implants.v1'

	webbrowser.open(login_url, new=0, autoraise=True)

	access_token = input("Give your access token: ")
	
	character_info = get_char_info(access_token)
	if character_info == 'error':
		return
	else:
		import_characters(access_token, character_info)
	
	return

	
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

	
def import_characters(access_token, character_info):
	print('importing character')
	#Load saved skill names and implant names
	try:
		item_id = json.load(open('item_id.txt'))
	except (IOError, json.decoder.JSONDecodeError):
		#Some error. Just start the id list from scratch
		item_id = {}
		with open('item_id.txt', 'w') as outfile:
			json.dump(item_id, outfile, indent=4)
		
	character_name = character_info['character_name']
	character_id = character_info['character_id']
	#access_token = access_token
		
	print('importing '+character_name+'...')
		
			
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

	return
	
	
	
#---------------------------
#Start the actual script now
#---------------------------

print('\nESI API importer for EFT by Hirmuolio Pine')

#Check if client ID and client secret are in the onfiguration file.
#If not ask for them and write them to the file.

client_id = '1a70477e32354a67a35343c693ed4243'

while True:
	input("Press enter to start importing")
	logging_in()

print('Imprt completed')
if has_errors == True:
	input("There were errors. Press enter to exit...")
