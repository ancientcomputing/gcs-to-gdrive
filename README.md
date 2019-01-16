# gcs-to-gdrive

In order to create the right structure of download/upload and the VMs and their drives, you should run the bash script create_plan.bash

It will not retreive back any information other than sizes and quantities of objects in the given bucket
NO information is being sent anywhere other than the output file and the shell standard output 

In order to asses the size of transfer from the Google Cloud Storage run the following command:

$  bash create_plan.bash BUCKET_NAME OUTPUT_FILE

argumant 1 = BUCKET_NAME (example: gs://amiteinav-bucket)
argument 2 = OUTPUT_FILE (example: ~/output.txt)

An example of running the file create_plan.bash :

$  bash create_plan.bash  gs://amiteinav-bucket output.txt

The expected output structure is:

2019-01-03 01:03:44|info|temp_file is: /tmp/file42582
2019-01-03 01:03:44|info|running gsutil ls -rl gs://amiteinav-sandbox | grep gs:// > /tmp/file42582
size of download is 286533158979 bytes
amount of files is 43784
amount of folders is 4832
list of files is at /tmp/file42582
9227 files in range of a KB totaling 4133887 bytes
33896 files in range of a MB totaling 1587384052 bytes
654 files in range of a GB totaling 27684244848 bytes
3 files in range of a 10GB totaling 1917408594 bytes
1 files in range of more than 10GB totaling 252497100800 bytes
