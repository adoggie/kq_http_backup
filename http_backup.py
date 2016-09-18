# -*- coding:utf-8 -*-
#auto backup system database 
#自动登录，http下载，压缩之后通过网盘同步到服务器
#如果下载中途被终止，那我们可以通过执行redo.bat继续下载，axel是断点续载滴
#要求时钟比交易服务器调慢10分钟

import httplib, urllib,sys,os,re,datetime,time,os.path,gzip

host="192.168.1.106"
host="kqgjls.net"
sys_user='da1yue'
sys_pass='yuxi23'
sys_user='zhang'
sys_pass='kqit002'
html = '''<body><h1>Object Moved</h1>This object may be found <a HREF="shuju.asp?err=
ok!&amp;dizhi=../data_backup/zhk0432011-1-26.7055475.mdb">here</a>.</body>
'''


tasklet=[]
backupTimes= 4 # in day 由于服务器时钟可能与本地不同步，导致在23:58分的时候同步还是前一天的数据文件（文件很大，只有过了0:0才产生新的小的数据库备份文件）
   #所以同步的客户机时钟尽可能调慢一点，比如相差个10分钟
excludeTimeRange=[()] #排外的时间段区间，时间落在其任何一时间段内将不执行下载备份
enableSwitchUrl='/backup.txt' #每次备份检测标志文件，如果访问失败则停止备份

def enableBackupByTimeRange(hour):
	return True

#检测当前是否允许备份	
def enableBackupBySwitch():
	r = True
	return True
	try:
		conn = httplib.HTTPConnection('114.80.100.189',8088)	
		conn.request("GET",enableSwitchUrl)
		resp = conn.getresponse()
		if resp.status != 200:
			r = False
		conn.close()
	except:
		r = False
	return r

def backup(outputfile):
	print 'Backup starting...'
	params = urllib.urlencode({'huiyuan_name':sys_user, 'huiyuan_pass': sys_pass, 'submit.x': 9,'submit.y':9})
	conn = httplib.HTTPConnection(host)
	headers = {"Content-type": "application/x-www-form-urlencoded",
				"Accept": "text/plain"}
	conn.request("POST","/asp/huiyuan/login_check_gl.asp",params,headers)
	resp = conn.getresponse()
	#print resp.status,resp.reason
	print resp.getheaders()
	cookie = resp.getheader('set-cookie')
	#print resp.read()
	conn.close()

	print 'retry GET /'
	conn = httplib.HTTPConnection(host)
	headers = {"Content-type": "application/x-www-form-urlencoded",
				"Accept": "text/plain",'Cookie':cookie}

	conn.request("GET","/asp/admin/login_check001.asp",'',headers)
	resp = conn.getresponse()

	#sys.exit(0)
	conn = httplib.HTTPConnection(host)
	headers = {"Content-type": "application/x-www-form-urlencoded",
				"Accept": "text/plain",'Cookie':cookie}
	
	backupfile = 'zhk0432011-1-25.7055475.mdb'
	if True:
		backupfile = ''
		conn.request("GET","/asp/admin/backup.asp",'',headers)
		resp = conn.getresponse()
		print resp.status,resp.reason
		html=  resp.read()

		m = re.search(".*?/data_backup/(.*?\.mdb).*",html)
		
		if len(m.groups()):
			backupfile = m.groups()[0]
			print backupfile
		else:
			print 'backup access failed!'
			return False
	
# -o wget.log
	#downloadurl= "http://%s/asp/data_backup/%s  -O %s "%(host,backupfile,outputfile)
	downloadurl= "http://%s/asp/data_backup/%s "%(host,backupfile)
	
	#print 'try get %s ...'%downloadurl
	#cmd = "wget -c -t 0 %s"%downloadurl
	cmd = "axel\\axel.exe  -o %s %s"%(outputfile,downloadurl)
	f= open('redo.bat','w')
	f.write(cmd)
	f.close()
	print cmd
	os.system(cmd)
	return True

firsttime = datetime.datetime.now()
if not os.path.exists('./backup'):
	os.mkdir('backup')
	
if not os.path.exists('./sync'):
	os.mkdir('sync')



	
while True:	
	if not enableBackupBySwitch():
		print 'system backup disabled!'
		time.sleep(10) #
		continue

	now = datetime.datetime.now()
	#filename = "backup/%s_%s-%s_%s_%s_%s.bak"%(now.year,now.month,now.day,now.hour,now.minute,now.second)	
	sync_hour= int(now.hour/int(24/backupTimes)) * int(24/backupTimes)  #这里加1是为了消除与服务器的误差，避免过早备份请求备份的是增量备份的文件名称
	filename = "%s_%s-%s_%s_%s_%s.bak"%(now.year,now.month,now.day,sync_hour,0,0)	
	try:
		if not os.path.exists("backup/"+filename):		
			backup("backup/"+filename)
			cmd = "7zip\\7z.exe a -t7z  sync\\%s.7z backup\\%s"%(filename,filename)
			print cmd
			os.system(cmd)	
	except:
		pass

	time.sleep(10) #

