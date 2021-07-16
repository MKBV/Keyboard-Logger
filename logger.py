import struct, keymap

event = open("/dev/input/event3", "rb")
inpt = event.read(24)
chk = ['a']


while inpt:
	(uts, msec, typ, code, value) = struct.unpack('llhhi', inpt)

	if typ == 1:
		chk.append(code)
		if chk[-1] != chk[-2]:
			print(keymap.char[code], end='', flush=True)
		else:
			chk = ['a']
			
	elif typ == 17:
		if value == 1: print("ON", end='', flush=True)
		elif value == 0: print("OFF", end='', flush=True)
		
	elif (typ == 4 and code == 4) or typ == 0:
		pass
	else:
		print("type:%d code:%d value:%d" % (typ,code,value))
	inpt = event.read(24)
event.close()
