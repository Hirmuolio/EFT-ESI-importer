# EFT-ESI-importer

This script will import your character skills and implants from ESI api and save them for EFT to use.
Place the scripts in characters folder in your EFT installation.

There are two versions of the script:
*  	`EFT_ESI_importer.py` is the full version that you should use first.
*  	`fast_EFT_ESI_importer.py` skips all the configuring steps and runs the importing without asking anything. You need to use the full version first to register and log in.

To use the script you need to register as a developer at https://developers.eveonline.com/ (requires EVE char that has had paid subscription at some point). You need to register an application with following scopes. `esi-skills.read_skills.v1` and
`esi-clones.read_implants.v1`. Set the callback url to `    http://localhost/oauth-callback ` The script will use the client ID and secret key of your registered application.

The script will ask for your authentication code when you log in. When you log in you are redirected to an adress that contains the authentication code.
`http://localhost/oauth-callback?code=[this is your authentication code]`

The script will import your effective skill levels. So if you are alpha with omega skills the script will only import your alpha skills.

Requirements: 
* Python 3.6 or newer
* Requests http://docs.python-requests.org/en/master/
