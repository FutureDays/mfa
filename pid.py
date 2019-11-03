import psutil
import os
pid = os.getpid()
ppid = psutil.Process(pid).ppid()
with open("/developments/mfa/logs/pids.log", 'a') as out:
	out.write(str(pid)+"/n")
	out.write(psutil.Process(pid).name()+"/n")
	out.write(str(ppid)+"/n")
	out.write(psutil.Process(ppid).name()+"/n")

