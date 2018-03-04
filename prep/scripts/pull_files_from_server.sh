#!/bin/bash

echo "starting"

get_files_from_server(){
	declare -a flist=$1
	for i in "${flist[@]}"
	do
		echo $i
		scp "brnco@mftest.hopto.org:${i}" $2
	done
}

delete_passwords(){
	pushd $1
	pwdfile="/Volumes/thedata/developments/mfa/scripts/passwords"
	while IFS= read -r pwd
	do
		echo "$pwd"
		for f in *
		do
			echo "$f"
			sed -e 's/$pwd//g' $f
			rm "${f}-e"
		done
	done < "$pwdfile"	
	popd
}

declare -a flist_config=("/etc/fstab" "/etc/*-release")
endDir1="/Volumes/thedata/developments/mfa/server_files/config"

get_files_from_server $flist_config $endDir1
delete_passwords $endDir1
