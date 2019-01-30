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
* run the following commands from the cloud console
```
export PROJECT_NAME=name-of-project
export VM_NAME=gcs-to-drv-instance
export VM_NAME=${VM_NAME}-${RANDOM}


gcloud compute instances create ${VM_NAME} --zone=us-central1-c --project=${PROJECT_NAME}  \
--machine-type=n1-standard-4 --subnet=default --network-tier=PREMIUM \
--maintenance-policy=MIGRATE \
 --scopes=https://www.googleapis.com/auth/cloud-platform --tags=gcs-to-drive \
 --boot-disk-size=500GB --boot-disk-type=pd-ssd \
 --boot-disk-device-name=${VM_NAME}-disk

```

### Setting up the python packages ###

* get the file to execute
```
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install git -y

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py

git clone https://github.com/amiteinav/gcs-to-gdrive.git

export BUCKET_ID=your-bucket-id
export PROJECT_NAME=your-project

cd gcs-to-gdrive

pip install -r requirements.txt --user
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
