#!/usr/bin/python

from esxiauto import VMESXiAuto
import ConfigParser
import subprocess
import os,time

#Read the esxi.conf file,to get the username passwd and malware path etc..
config = ConfigParser.ConfigParser()
config.readfp(open("esxi.conf"))
host_username = config.get("host","username")
host_passwd = config.get("host","passwd")
malware_path = config.get("malware","path")

#Get the malware files list
malware_list = subprocess.Popen(
			['find',malware_path,'-type','f'],
			stdout = subprocess.PIPE
			)
malware_file_list = malware_list.communicate()[0]

#running Flag
running = False

for malware_file in malware_file_list:
	if not running:
		#whether running
		running = True
		
		#select you VM to work with
		vm = VMESXiAuto("[ha-datacenter/datastore1 (1)] 142-ubuntu11.04_xmpp/142-ubuntu11.04_xmpp.vmx")

		#revert to the snapshot
		vm.revert('cleanimg')

		#start the VM running
		vm.start()
		time.sleep(15)

		#set the user and passwd for Host
		vm.set_Hostuser(host_username,host_passwd)
	
		#Get malware file name
		#malware_file_name = os.path.split(malware_list)[-1]
		dst = 'C:\\%s' % os.path.basename(malware_file_name)
	
		#copy the malware to a path on the VM
		vm.copytovm(malware_file,dst)#"c:\\"+malware_file_name)

		#execute the malware
		vm.winexec(dst)#"c:\\"+malware_file_name)
		time.sleep(60)
	
		vm.suspend()
		
		#Mark the VM Guest is idle
		running = False
	
	
