#!/usr/bin/env python3

import requests
import json
import webbrowser
import base64

#---------------------------
#Define functions
#---------------------------
	
#Use refresh token to get new access token
def refresh_auth(refresh_token):
	refresh_url = 'https://login.eveonline.com/oauth/token'
	
	combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
	esi_response = requests.post(refresh_url, headers =  {"Authorization":"Basic "+combo}, data = {"grant_type": "refresh_token", "refresh_token": refresh_token} )
	
	if esi_response.status_code == 200:
		access_token = esi_response.json()['access_token']
	else:
		print('Refreshing acces token. Error',esi_response.status_code,'-', esi_response.json()['error'])
	return access_token
	
#Get info on the character by using the access token
def get_char_info(access_token):
	
	url = 'https://login.eveonline.com/oauth/verify'
	esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
	
	if esi_response.status_code == 200:
		response = esi_response.json()
		character_id = response['CharacterID']
		character_name = response['CharacterName']
		character_info = {"character_id":character_id, "character_name":character_name}
	else:
		print('Getting char info. Error',esi_response.status_code,'-', esi_response.json()['error'])
	return character_info

	
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
			
			#Import skills and put them in the string
			#import implants and put them to same string
			#Write the string to file and be done
			
			output = ''
			
			#Import skills first
			url = 'https://esi.tech.ccp.is/v4/characters/'+str(character_id)+'/skills/?datasource=tranquility'
			
			esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
			if esi_response.status_code != 200:
				print(esi_response.status_code,'-', esi_response.json()['error'], '- skills for character: '+character_name)
			else:
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
			
			url = 'https://esi.tech.ccp.is/v1/characters/'+str(character_id)+'/implants/?datasource=tranquility'
			
			esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
			if esi_response.status_code != 200:
				print(esi_response.status_code,'-', esi_response.json()['error'], '- implants for character: '+character_name)
			else:
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
		print('no client ID or secret found. \nUse the full script')

except (IOError, json.decoder.JSONDecodeError):
	print('no client ID or secret found. \nUse the full script')

run = True
while run:
	import_characters()

print('Imprt completed')
