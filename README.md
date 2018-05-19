# EFT-ESI-importer

This script will import your character skills and implants from ESI api and save them for EFT to use.
Place the scripts in characters folder in your EFT installation.

There are two versions of the main script:
*  	`EFT_ESI_importer.py` is the full version that you should use first.
*  	`fast_EFT_ESI_importer.py` skips all the configuring steps and runs the importing without asking anything. You need to use the full version first to register and log in.

To use the script you need to register as a developer at https://developers.eveonline.com/ (requires EVE char that has had paid subscription at some point). You need to register an application with following scopes. `esi-skills.read_skills.v1` and
`esi-clones.read_implants.v1`. Set the callback url to `    http://localhost/oauth-callback ` The script will use the client ID and secret key of your registered application.

The script will ask for your authentication code when you log in. When you log in you are redirected to an adress that contains the authentication code.
`http://localhost/oauth-callback?code=[this is your authentication code]`

When you import for the first time the script will fetch names of all your skills and implants from ESI API. This may take a while. The names are saved loaclly so this will happen only when a skill is encountered for the first time.

The script will import your effective skill levels. So if you are alpha with omega skills the script will only import your alpha skills.

### Implicit version

There is also a third script `EFT_ESI_importer_implicit.py`. This version is meant for those who can not register as application developers. If you can register as an application developer the other two are much better.

This version of the script uses implicit grant authorization flow instead of the other one. The result is that no refresh token is aquired and the login expires in 20 minutes. This will require you to log in every time you import skills. The script includes  client ID from me so you dont' need to register as application developer to use it.

When you log in through this version you will be redirected to `http://localhost/oauth-callback#access_token=[token is here]&token_type=Bearer&expires_in=1199`. Copy the token to the commandline and your skills are impoted.

## Requirements: 
* Python 3.6 or newer
* Requests http://docs.python-requests.org/en/master/
