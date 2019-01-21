#!/usr/bin/env python

'''
pip install --user google.cloud.storage
pip install --user google.cloud.resource.manager

-p project-id   # the relevant project-id
-b bucket       # the relevant bucket-name
-i              # indicator if this is to get information only
-c tsv-file     # tab seperated file containing the entire repository of the gcs bucket
-n file         # file with information about the bucket (amount of files, storage classes amount)
-s              # indicator to skip the check if the project exists
-d              # download



time python download_from_gcs.py -b test-for-drive -p amiteinav-sandbox -d -s -i

xxx
'''

from google.cloud import storage
from google.cloud import resource_manager
import os, sys, urllib2, json, random, getopt, base64, csv, datetime, multiprocessing, time, ast


# Import Google libraries
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFileList
import googleapiclient.errors

root_folder='gcs-drive'


def message(msg, level="Info"):
    logfile = '/tmp/offload_gcs_to_drive.log'
    now = datetime.datetime.now()
    time =  now.isoformat()
    str = level + "|" + time + "|" + msg + "\n"
    with open(logfile, "a") as myfile:
        myfile.write(str)
        myfile.close()
    if (level == "Error"):
        print (str)
    elif (level == "Usage"):
        print (msg)

def download_blob2(bucket_name, source_blob_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(source_blob_name)
    filename=str(random.randint(1,9223372036854775807))+'.temp'
    blob.download_to_filename(filename)
    return filename

def create_bucket(bucket_name):
    """Creates a new bucket."""
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    print('Bucket {} created'.format(bucket.name))

def project_exists(project):
    message('checking if project {} exists'.format(project))
    client = resource_manager.Client()
    for project_name in client.list_projects():
        if ( project_name.name == project ):
            return True
    return False

def bucket_exists(bucket, project):
    storage_client = storage.Client(project)
    try:
        bucket = storage_client.get_bucket(bucket)
    except google.cloud.exceptions.NotFound:
        message ('the bucket {} was not found'.format(bucket))
        return False
    return True

def get_file_id_status(file_id,status_file):
    message ('Now checking file id: {}'.format(file_id))
    if (not os.path.exists(status_file)):
        return 'NOT_STARTED'

    with open(status_file, "rU") as in_file:
        reader = csv.DictReader(in_file,delimiter='\t')
        for row in reader:
            if ( row['id'] == file_id ):
                return row['status']
    return 'NOT_STARTED'

def get_temp_file_name(id_no,status_file):
    with open(status_file, "rU") as in_file:
        reader = csv.DictReader(in_file,delimiter='\t')
        for row in reader:
            if ( row['id'] == id_no ):
                return row['temp_file']
    return 'none'


# counting lines in a file - works slower than simplecount
def bufcount(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    return lines

def simplecount(filename):
    lines = 0
    for line in open(filename):
        lines += 1
    return lines    


def get_folder_id(drive, parent_folder_id, folder_name):
    """ 
        Check if destination folder exists and return it's ID
    """

    # Auto-iterate through all files in the parent folder.
    file_list = GoogleDriveFileList()
    try:
        file_list = drive.ListFile(
            {'q': "'{0}' in parents and trashed=false".format(parent_folder_id)}
        ).GetList()
    # Exit if the parent folder doesn't exist
    except googleapiclient.errors.HttpError as err:
        # Parse error message
        message = ast.literal_eval(err.content)['error']['message']
        if message == 'File not found: ':
            #print(message + folder_name)
            exit(1)
         #Exit with stacktrace in case of other error
        else:
            raise

    # Find the the destination folder in the parent folder's files
    for file1 in file_list:
        if file1['title'] == folder_name:
            #print('title: %s, id: %s' % (file1['title'], file1['id']))
            return file1['id']

def create_folder(drive, folder_name, parent_folder_id):
    """ 
        Create folder on Google Drive
    """

    folder_metadata = {
        'title': folder_name,
        # Define the file type as folder
        'mimeType': 'application/vnd.google-apps.folder',
        # ID of the parent folder        
        'parents': [{"kind": "drive#fileLink", "id": parent_folder_id}]
    }

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    # Return folder informations
    #print('title: %s, id: %s' % (folder['title'], folder['id']))
    return folder['id']

def upload_file(drive,filename,folderid):

    message ('Now uploading file {}'.format(filename))

    #Upload file to folder
    file_drive = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folderid}]})
    file_drive.SetContentFile(filename)
    file_drive.Upload()

    message ('File {} uploaded'.format(filename))

def resumable_download_operation(proc_id,queue,status_file,csvfile,line_no_start,line_no_end,drive):
    message('starting the function resumable_download_operation {}'.format(proc_id))
    if (not os.path.exists(status_file)):
        write_header = True
    else:
        write_header = False

    status_header = 'id\ttemp_file\tstatus\n'

    index = 0

    with open(csvfile, "rU") as in_file:
        reader = csv.DictReader(in_file,delimiter='\t')
        for row in reader:
            if ((index >= line_no_start) and (index <= line_no_end) ):
                id_no = row['id']
                fullpath= row['fullpath']
                folder_name=row['folder']
                filename=row['filename']
                #id_no,size,storage_class,md5_hash,folder,filename,fullpath=linecache.getline(csvfile,random_line_no).split('\t')

                curr_status = get_file_id_status(id_no,status_file)
                if (curr_status == 'NOT_STARTED'):
                    temp_file=download_blob2(id_no.split('/')[0], fullpath)
                    line=id_no+'\t'+str(temp_file)+'\t'+'DOWNLOADED'+'\n'
                    with open(status_file,'a+') as out_file:
                        if (write_header):
                            out_file.write(status_header + '\n')
                        out_file.write(line)
                elif (curr_status == 'DOWNLOADED'):
                    temp_file=get_temp_file_name(id_no,status_file)
                # Now uploading to Google Drive
                #Create folder

                parent_folder_id = get_folder_id(drive, 'root', root_folder)

                for folder_itr in folder_name.split('/'):
                    message ('Now dealing with x{}x'.format(folder_itr))

                    if (folder_itr != '' and folder_itr != ' '):

                        message ('folder itr = {}'.format(folder_itr))
                        file_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(parent_folder_id)}).GetList()

                        found_folder = False

                        for file1 in file_list:
                            if ((file1['title'] == folder_itr) and (file1['mimeType'] == 'application/vnd.google-apps.folder')):
                                message ('found folder: {}'.format(folder_itr))
                                found_folder = True

                        if (not found_folder):
                            message('creating folder {}'.format(folder_itr))
                            parent_folder_id=create_folder(drive, folder_itr, parent_folder_id)
                        else:
                            message('Not creating folder {}'.format(folder_itr))
                            parent_folder_id = get_folder_id(drive, parent_folder_id, folder_itr)

                found_file = False

                message ('Checking if the file {} already exists in {}'.format(filename, fullpath))
                file_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(parent_folder_id)}).GetList()
                for file1 in file_list:
                    #message ('file listed is: {} (lenght {}) with mimeType {} and compared against {} (lenght {})'.format(file1['title'],len(file1['title']),file1['mimeType'],filename,len(filename)))
                    if ((file1['title'] == filename) and (file1['mimeType'] != 'application/vnd.google-apps.folder')):
                        found_file=True
                        message ('File {} already exists in {}'.format(filename, fullpath))

                if (not found_file):
                    message('Now dealing with the file {} of path {}'.format(filename,fullpath))
                    message('Changing name of file {} to {}'.format(temp_file, filename))
                    os.rename(temp_file, filename) 
                    upload_file(drive,filename,parent_folder_id)

                    os.remove(filename)

            index =+ 1

    queue.put(1)
    message ('finished running resumable_download_operation {}'.format(proc_id))

def download_operation(status_file,csvfile):

    g_login = GoogleAuth()
    g_login.LocalWebserverAuth()
    drive = GoogleDrive(g_login)

    lines_in_csvfile=simplecount(csvfile)
    message ('the file {} has {} lines'.format(csvfile,lines_in_csvfile))

    running_processes=0
    target_running_processes=10

    queue = multiprocessing.Queue()
    line_no_start=0
    

    if (lines_in_csvfile <= target_running_processes):
        target_running_processes=1
        line_no_end=lines_in_csvfile
        lines_per_worker=lines_in_csvfile
    else:
        lines_per_worker = lines_in_csvfile / target_running_processes
        mod_lines_per_worker = lines_in_csvfile % target_running_processes    
        # Added the modulus to the first worker
        line_no_end=lines_per_worker+mod_lines_per_worker

    message ('about to run {} workers, each with {} lines'.format(target_running_processes,lines_per_worker))

    for i in range(0, target_running_processes):
        message('now running subprocess number {} the range of {} to {}'.format(i,line_no_start,line_no_end))
        multiprocessing.Process(target=resumable_download_operation, args=[i,queue,status_file,csvfile,line_no_start,line_no_end,drive]).start()
        #resumable_download_operation(status_file,csvfile,line_no_start,line_no_end)
        line_no_start=line_no_end+1
        line_no_end+=lines_per_worker

    message ('finished spawning the processes, now waiting for them to finish')
    stop_waiting = False
    count=0

    while ( not stop_waiting ):
        number = queue.get()
        count+=number
        message ('the amount of processes finished so far is {}'.format(count))
        if (count == target_running_processes) :
            stop_waiting = True
        time.sleep(5)

    return True


def set_bucket_information(bucket, project,csv_list,information_file):
    
    message ('getting bucket {} of project {} information'.format(bucket,project))
    storage_client = storage.Client(project)
    bucket_obj = storage_client.get_bucket(bucket)

    # emptying the file 
    open(csv_list, 'w').close()

    lines_to_flush=1000
    lines_itr=0

    blob_list = bucket_obj.list_blobs()
    header='id\tsize\tstorage_class\tmd5_hash\tfolder\tfilename\tfullpath\n'
    lines=header
    
    size_categories = ['KB', 'MB', 'GB','10GB','multiGB','Total']
    size_figures = [0,0,0,0,0,0]
    size_count = [0,0,0,0,0,0]

    storage_classes = ['MULTI_REGIONAL', 'REGIONAL', 'NEARLINE','COLDINE','STANDARD','DURABLE_REDUCED_AVAILABILITY']
    classes_figures = [0,0,0,0,0,0]
    classes_count = [0,0,0,0,0,0]


    for bo in blob_list:

        curr_size=int(bo.size)

        lines+=bo.id.encode('ascii', 'ignore').decode('ascii')+'\t'
        lines+=str(curr_size)+'\t'
        lines+=bo.storage_class+ '\t'
        lines+=str(bo.md5_hash)+'\t'
        path=bo.name.encode('ascii', 'ignore').decode('ascii')
        str(path)
        if (path.find('/')>0):
            folder=path[0:len(path)-len(path.split('/')[-1])]
            file_name=path.split('/')[-1]
        else:
            folder='/'
            file_name=path
        lines+=folder+'\t'
        lines+=file_name+'\t'
        lines+=path+'\n'


        classes_count[storage_classes.index(str(bo.storage_class))]+=1
        classes_figures[storage_classes.index(str(bo.storage_class))]+=curr_size

        if ((0<=curr_size) and (curr_size<=1024)):
            size_index=size_categories.index(str('KB'))
        elif ((1025<=curr_size) and (curr_size<=1048576)):
            size_index=size_categories.index(str('MB'))
        elif ((1048577<=curr_size) and (curr_size<=1073741824)):
            size_index=size_categories.index(str('GB'))
        elif ((1073741825<=curr_size) and (curr_size<=10737418240)):
            size_index=size_categories.index(str('10GB'))
        else:
            size_index=size_categories.index(str('multiGB'))
        
        size_figures[size_index]+=curr_size
        size_count[size_index]+=1

        size_figures[size_categories.index(str('Total'))]+=curr_size
        size_count[size_categories.index(str('Total'))]+=1

        lines_itr+=1

        if (lines_itr == lines_to_flush ):
            lines_itr=0
            open (csv_list,"a+").write(lines)
            lines=''
    open (csv_list,"a+").write(lines)

    info_line=''

    for a,b,c in zip(size_categories, size_figures, size_count):
        info_line+= '{0} {1}-files. totalling {2} bytes\n'.format(c,a,b)
        print('{0} {1}-files. totalling {2} bytes'.format(c,a,b)) 


    for a,b,c in zip(classes_count, storage_classes, classes_figures):
        info_line+='{0} {1} files. totalling {2} bytes\n'.format(a,b,c)
        print('{0} {1} files. totalling {2} bytes'.format(a,b,c)) 

    open(information_file,"w").write(info_line)



def main(argv):

    set_information = False
    csvfile='gcs-inventory.tsv'
    information_file='gcs-stats.info'
    skip_project_check = False
    start_download = False
    status_file='status.csv'

    try:
        opts, args = getopt.getopt(argv,"p:b:in:c:sd")
    except getopt.GetoptError:
        sys.exit(42)
    for opt, arg in opts:
        if opt == "-p":
            project = arg
        elif opt == "-b":
            bucket = arg
        elif opt == "-i":
            set_information = True
        elif opt == '-c':
            csvfile = arg
        elif opt == '-n':
            information_file = arg
        elif opt == '-s':
            skip_project_check = True
        elif opt == '-d':
            start_download = True

    if (not skip_project_check):
        if (not project_exists(project)):
            print ('no such project {}'.format(project))
            exit(42)

    if (not bucket_exists(bucket,project)):
        print ('no such bucket {} in project {}'.format(bucket,project))
        exit(42)

    message ('project: {}, bucket: {}, set_information? {}'.format(project,bucket,set_information))

    if ( set_information ):
        set_bucket_information(bucket, project,csvfile,information_file)

    if (start_download):
        download_operation(status_file,csvfile)


if __name__ == "__main__":
    script_name=sys.argv[0]
    arguments = len(sys.argv) - 1

    if (arguments == 0):
        sys.exit(42)

    main(sys.argv[1:])
