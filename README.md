# Copying files from google cloud storage to Google Drive

The following steps are required for setting up the envrionment for copying an entire bucket from Google Cloud storage to a Google Drive

## Important ##

* The landing area in Google Drive would be **gcs-drive** and it **must** exists prior to running the script. to change the name of gcs-drive to a different name, change the value of global parameter **root_folder**

## Steps to set-up ##

### Creating a ‘client_secrets.json’ ###

* Go to your Google developers console (https://console.developers.google.com/apis/credentials). 
* You should see a section titled OAuth 2.0 client IDs. Click on an entry in that list, and you will see a number of fields, including Client secret.
* If you have not yet created credentials, click the Create credentials button, and follow the instructions to create new credentials, and then follow the steps outlined above to find the Client secret.


