'''
mfa-pre-sip-cleanup
'''
import os
import shutil

class dotdict(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def move():
	if dct.transcodeq:
		dest = dct.transcodest
	else:
		dest = dct.compounded
	shutil.move(dct.sfullpath, dest)

def verifys():
	dct.scool = True
	with cd(dct.sfullpath):
		for f in os.listdir(os.getcwd()):
			if not f.endswith(".WAV") and not f.endswith(".wav") and not f.endswith(".DS_Store") and not f.endswith(".MP3") and not f.endswith(".mp3"):
				dct.scool = False
				if f.endswith(".aiff") or f.endswith (".AIFF"):
					dct.transcodeq = True

def main():
	'''
	got to
	scan each directory for things that are not WAV
	for any copy.WAV
	-hash it and compare
	is in cataloguing - update inventory too
	any directory that doesnt pass tests gets moved

	'''
	global dct
	tld = "/Volumes/feinstein_2014-2017_clone/"
	yr = "2017"
	for dirs, subdirs, files in os.walk(os.path.join(tld,yr)):
		for s in subdirs:
			if s.startswith("."):
				continue
			dct = dotdict({})
			dct.tldir = tld
			dct.yr = yr
			dct.sfullpath = os.path.join(dct.tldir,dct.yr,s)
			dct.transcodest = os.path.join(dct.tldir,"transcodes")
			dct.compounded = os.path.join(dct.tldir, "compounded-objects")
			verifys()
			#print dct
			if dct.scool is False:
				print s
				foo = raw_input("eh")
				move()
			else:
				pass

main()
