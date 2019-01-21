# Copying files from google cloud storage to Google Drive

The following steps are required for setting up the envrionment for copying an entire bucket from Google Cloud storage to a Google Drive

## Important ##

* The landing area in Google Drive would be **gcs-drive** and it **must** exists prior to running the script. to change the name of gcs-drive to a different name, change the value of global parameter **root_folder**

## Steps to set-up ##

### Creating a ‘client_secrets.json’ ###

* Go to your Google developers console (https://console.developers.google.com/apis/credentials). 
* You should see a section titled OAuth 2.0 client IDs. Click on an entry in that list, and you will see a number of fields, including Client secret.
* If you have not yet created credentials, click the Create credentials button, and follow the instructions to create new credentials, and then follow the steps outlined above to find the Client secret.

* If the instructions above are not clear - please follow this step by step: https://o7planning.org/en/11917/create-credentials-for-google-drive-api


### Creating a virtual machine ###
* run the following command from the cloud console
```
gcloud compute --project=amiteinav-sandbox instances create gcs-to-drv-instance --zone=us-central1-c --machine-type=n1-standard-4 --subnet=default --network-tier=PREMIUM --maintenance-policy=MIGRATE --service-account=951308682803-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --tags=gcs-to-drive --image=debian-9-drawfork-v20181101 --image-project=eip-images --boot-disk-size=900GB --boot-disk-type=pd-ssd --boot-disk-device-name=gcs-to-drv-instance
```

### Setting up the python packages ###

* get the file to execute
```
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install git -y

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

git clone https://github.com/amiteinav/gcs-to-gdrive.git

pip install -r requirements.txt --user

export BUCKET_ID=your-bucket-id
export PROJECT_NAME=your-project

cd gcs-to-gdrive

pip install -r requirements.txt 
```
### Placing the ‘client_secrets.json’ ###

* You will need to place the file **client_secrets.json** in this folder. 

* One way to do is uploading it into a Google Cloud Storage and downloading it in the VM

* from the local host you run 
```
gsutil cp client_secrets.json gs://${BUCKET_ID}
```


* from the GCE VM you run 
```
gsutil cp  gs://${BUCKET_ID}/client_secrets.json .
```

## Now you are ready to start copying to Drive from GCS ##

### run ###

The first run:
```
nohup time python download_from_gcs.py -b ${BUCKET_ID} -p ${PROJECT_NAME} -d -i &
```

There could be a very slow transfer - Google Drive is heavier..

to resume run:
```
rm gcs-inventory.tsv gcs-stats.info status.csv *.temp

nohup time python download_from_gcs.py -b ${BUCKET_ID} -p ${PROJECT_NAME} -d -s -i &
```

### troubleshoot ###
for questions - please email me at amiteinav@google.com
make sure to provide the **log file** with your question(s) - **/tmp/offload_gcs_to_drive.log** 
