#!/usr/bin/python

import os
import sys
import subprocess
import pexpect

machineList = []
goodList = []
machineCfg = 'machines'

def readCfg(cfg):
	f = open(cfg, 'r')
	cfgContent = f.readline()
	while cfgContent != '':
		if cfgContent[0] == '#':
			cfgContent = f.readline()
		else:
			cfgContent = cfgContent.split()
			if len(cfgContent) == 4:
				machineList.append(cfgContent)
			cfgContent = f.readline()
	f.close()
	print "Machine List: %s" % machineList
	print "========================================"

def deleteHosts():
	print "Deleting known_hosts"
	if os.path.isfile('.ssh/known_hosts'):
		if os.path.isfile('.ssh/known_hosts.bak'):
			print "delete ~/.ssh/known_hosts"
			os.remove('.ssh/known_hosts')
		else:
			print "rename ~/.ssh/known_hosts"
			os.rename(".ssh/known_hosts", ".ssh/known_hosts.bak")

def detectSSH():
	ssh_newkey = 'Are you sure you want to continue connecting'
	for i in range(0, len(machineList)):
		print "Current prefix: ", machineList[i][0]
		for j in range(int(machineList[i][2]), int(machineList[i][3])+1):
			machine = machineList[i][0] + "%02d"%j + machineList[i][1]
			cmd = '''ssh -o ConnectTimeout=1 ''' + machine + " 'ls -l /dev/console'"
			p=pexpect.spawn(cmd)
			k=p.expect([ssh_newkey, pexpect.EOF])
			if k==0:
				print machine
				checkOwnerSingle(machine)
				#goodList.append(machine)
			p.terminate()
	#print "Live Linux host: %s" % goodList
				
def runSSHCmd(cmd):
	# http://linux.byexamples.com/archives/346/python-how-to-access-ssh-with-pexpect/
	ssh_newkey = 'Are you sure you want to continue connecting'
	p=pexpect.spawn(cmd)
	i=p.expect([ssh_newkey,'password:',pexpect.EOF])
	if i==0:
		p.sendline('yes')
		i=p.expect([ssh_newkey,'password:',pexpect.EOF])
	elif i==1:
		print "Need password"
	elif i==2:
		pass
	print p.before.splitlines()[-1] # print out the result
	p.terminate()

def checkOwnerSingle(x):
	runSSHCmd("ssh " + x + ''' "ls -l /dev/console  | awk '{print $3}'"''')

def checkOwner():
	for m in range(0, len(goodList)):
		print goodList[m]
		checkOwnerSingle(goodList[m])

def checkCPUSingle(x):
	runSSHCmd("ssh " + x + ''' "cat /proc/cpuinfo | grep 'model name' | head -n 1"''')

def checkCPU():
	for m in range(0, len(goodList)):
		print goodList[m]
		checkCPUSingle(goodList[m])

def restoreHosts():
	print "Restoring known_hosts"
	if os.path.isfile('.ssh/known_hosts.bak'):
		if os.path.isfile('.ssh/known_hosts'):
			os.remove('.ssh/known_hosts')
		os.rename('.ssh/known_hosts.bak', '.ssh/known_hosts')

def main():
	readCfg(machineCfg)
	deleteHosts()
	try:
		detectSSH()
	except KeyboardInterrupt:
		restoreHosts()
	else:
		restoreHosts()

if __name__ == "__main__":
    main()
