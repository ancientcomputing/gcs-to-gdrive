#!/bin/bash

# $1 = bucket_path
# 
# $2 = plan_file

log_file="/tmp/plan_prep.log"

log() 
{
 TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
 echo "${TIMESTAMP}|$2|$1" >> ${log_file}
 if [ $# -eq 3 ] ; then
 	echo  "${TIMESTAMP}|$2|$1" 
 fi
}


if [ $# -eq 2 ] ; then
	bucket_path=$1
	plan_file=$2
else
	log "bucket_path: ${bucket_path}" "info" "console"
	log "plan_file: ${plan_file}" "info" "console"
fi

temp_file=/tmp/file$$
log "temp_file is: ${temp_file}" "info" "console"

log "running gsutil ls -rl ${bucket_path} | grep gs:// > ${temp_file}" "info" "console"
gsutil ls -rl ${bucket_path} | grep "gs://" > ${temp_file}

size=0
kbfiles=0 		# files in range of a KB
mbfiles=0 		# files in range of a MB
gbfiles=0 		#files in range of a GB
tengbfiles=0 	#files in range of a 10GB
multigbfiles=0
tkbfiles=0
tmbfiles=0
tgbfiles=0
ttengbfiles=0
tmultigbfiles=0


for i in `cat ${temp_file} | awk '{print $1}' | grep -v "gs://" ` ; do

size=$((size + i))
if ((0<=$i && $i<=1024))
then
	kbfiles=$((kbfiles+1))
	tkbfiles=$((tkbfiles+$i))
elif ((1025<=$i && $i<=1048576))
then
	mbfiles=$((mbfiles+1))
	tmbfiles=$((tmbfiles+i))

elif ((1048577<=$i && $i<=1073741824))
then
	gbfiles=$((gbfiles+1))
	tgbfiles=$((tgbfiles+i))

elif ((1073741825<=$i && $i<=10737418240))
then
	tengbfiles=$((tengbfiles+1))
	ttengbfiles=$((tengbfiles+i))

else
	multigbfiles=$((tengbfiles+1))
	tmultigbfiles=$((tmultigbfiles+i))

fi 

done

size=$size

files=`cat ${temp_file} | awk '{print $1}' | grep -v "gs://"  | wc -l | awk '{print $1}' `
folders=`cat ${temp_file} | awk '{print $1}' | grep "gs://"  | wc -l | awk '{print $1}' `

cat /dev/null > ${plan_file}

echo "size of download is ${size} bytes" >> ${plan_file}
echo "amount of files is ${files}" >> ${plan_file}
echo "amount of folders is ${folders}" >> ${plan_file}
echo "list of files is at ${temp_file}" >> ${plan_file}
echo "${kbfiles} files in range of a KB totaling ${tkbfiles} bytes" >> ${plan_file}
echo "${mbfiles} files in range of a MB totaling ${tmbfiles} bytes" >> ${plan_file}
echo "${gbfiles} files in range of a GB totaling ${tgbfiles} bytes" >> ${plan_file}
echo "${tengbfiles} files in range of a 10GB totaling ${ttengbfiles} bytes" >> ${plan_file}
echo "${multigbfiles} files in range of more than 10GB totaling ${tmultigbfiles} bytes" >> ${plan_file}

cat ${plan_file}



