import Tkinter
import tkMessageBox
import subprocess
import re
import random
import threading
import urllib, json
import time
import os.path


class spoofGUI(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()


	infolist = re.findall(
            r'^(?:Hardware Port|Device|Ethernet Address): (.+)$',
            subprocess.check_output((
                'networksetup',
                '-listallhardwareports'
            ), universal_newlines=True), re.MULTILINE
        )

	target = 'Wi-Fi'
	targetDevice = ''
	targetOriginalMac = ''

	for i in range(0, len(infolist), 3):
		if target in infolist[i]:
			targetDevice = infolist[i+1]
			targetOriginalMac = infolist[i+2]
	
	runTimer = False
	interval = 2.0

	options = []


	borderWidth = 2

	# create GUI elements
	def initialize(self):
		
		self.grid()

		#Header
		label = Tkinter.Label(self, text = "MacSpoofer", font=("Helvetica", "20"), padx="20", pady="10", justify="center")
		label.grid(row=0, columnspan=2)



		#Target Frame
		def sel(picked):
			self.target = picked
			for i in range(0, len(self.infolist), 3):
				if self.target in self.infolist[i]:
					self.targetDevice = self.infolist[i+1]
					self.targetOriginalMac = self.infolist[i+2]
			refreshInfoFrameExtra()
			updateLog()

		radioFrame = Tkinter.LabelFrame(self, padx=10, pady=10, text="Target Device", bd=self.borderWidth)
		radioFrame.grid(row=1, padx=10, columnspan=2, stick='ew', pady=5)

		menuVar = Tkinter.StringVar()
		
		for i in range(0, len(self.infolist), 3):
			self.options.append(self.infolist[i])
			if "Wi-Fi" in self.infolist[i]:
				menuVar.set(self.infolist[i])

		self.opMenu = Tkinter.OptionMenu(radioFrame, menuVar, *self.options, command=sel)
		self.opMenu.config(width=15)
		self.opMenu.grid(row=0, column=0, padx=10, rowspan=2)

		#MacAddress Info
		testLMac = Tkinter.Label(radioFrame, text="Orignal MacAddress:\nCurrent MacAddress:", justify='left')
		testLMac.grid(row=(0), column=1)
		testLMacNo = Tkinter.Label(radioFrame, text=self.targetOriginalMac + '\n' + self.targetOriginalMac, justify='left')
		testLMacNo.grid(row=(0), column=2)

		def refreshInfoFrame():
			for i in range(0, len(self.infolist), 3):
				if self.target in self.infolist[i]:
					mAddress = ''
					try:
						mAddress = subprocess.check_output(('ifconfig',self.infolist[i+1],'ether'))
						mAddress = mAddress[-19:-1]
					except subprocess.CalledProcessError:
						mAddress = self.infolist[i+2]
					testLMac.config(text="Orignal MacAddress:\nCurrent MacAddress:")
					testLMacNo.config(text=self.infolist[i+2] + '\n' + mAddress)
			threading.Timer(11, updateLog).start()
			
		def refreshInfoFrameExtra():
			for i in range(0, len(self.infolist), 3):
				if self.target in self.infolist[i]:
					mAddress = ''
					try:
						mAddress = subprocess.check_output(('ifconfig',self.infolist[i+1],'ether'))
						mAddress = mAddress[-19:-1]
					except subprocess.CalledProcessError:
						mAddress = self.infolist[i+2]
					testLMac.config(text="Orignal MacAddress:\nCurrent MacAddress:")
					testLMacNo.config(text=self.infolist[i+2] + '\n' + mAddress)



		
		#Password Frame
		passFrame = Tkinter.LabelFrame(self, padx=10, pady=10, text="Password", width=50, height=50, bd=self.borderWidth)
		passFrame.grid(row=2, column=0, sticky='news', pady=5, padx=10)

		self.password = Tkinter.StringVar()
		passE = Tkinter.Entry(passFrame, show='*', textvariable=self.password)
		passE.grid(row=0, column=0, pady=10)


			


		#Action Frame
		def randomizeMac():
			if self.targetDevice == '':
				tkMessageBox.showinfo("Randomize", "Please select a target above")
			else:
				spoof_mac_random(self.targetDevice, self.password.get())
				refreshInfoFrame()

		def resetMac():
			if self.targetDevice == '':
				tkMessageBox.showinfo("Randomize", "Please select a target above")
			else:
				spoof_mac_specific(self.targetDevice, self.targetOriginalMac, self.password.get())
				refreshInfoFrame()

		bFrame = Tkinter.LabelFrame(self, pady=10, text="Commands", bd=self.borderWidth)
		bFrame.grid(row=2, column=1, sticky='news', pady=5, padx=10)

		randomB = Tkinter.Button(bFrame, text="Randomize MacAddress", command=randomizeMac, width=20)
		randomB.grid(row=0, column=0, padx=10)

		resetB = Tkinter.Button(bFrame, text="Reset MacAddress", command=resetMac, width=20)
		resetB.grid(row=1, column=0, padx=10)




		#Timer frame
		tFrame = Tkinter.LabelFrame(self, padx=10, pady=10, text="Timed Randomize", bd=self.borderWidth)
		tFrame.grid(row=4, column=0, columnspan=2, stick="ew", padx=10, pady=5)

		
		def timedRandomize():
			if self.runTimer:
				print("MacChanged")
				spoof_mac_random(self.targetDevice, self.password.get())
				refreshInfoFrame()
				threading.Timer(self.interval*60, timedRandomize).start()

		def start_stop_timer():
			if self.targetDevice == '':
				tkMessageBox.showinfo("Randomize", "Please select a target above")
			else:
				if self.password.get() != '':
					self.interval = scaleVar.get()
					if self.runTimer:
						self.runTimer = False
						# for r1 in self.radioList:
						self.opMenu.config(state='active')
						self.timerB.config(text="Start Timed Randomiz")
					else:
						self.runTimer = True
						timedRandomize()
						# for r1 in self.radioList:
						self.opMenu.config(state='disabled')
						self.timerB.config(text="Stop Timed Randomiz")
				else:
					tkMessageBox.showinfo("Missing permission", "Please enter your password")

		def slider_move(value):
			self.timerL.config(text=value + " min")
			self.interval = scaleVar.get()

		scaleVar = Tkinter.DoubleVar()
		scale = Tkinter.Scale(tFrame, variable = scaleVar, orient='horizontal', length=180, from_=1, to=120, command=slider_move, showvalue=0)
		scale.grid(row=0, column=0, padx=5)

		self.timerL = Tkinter.Label(tFrame, text=scaleVar.get(), width=5)
		self.timerL.grid(row=0, column=1, padx=5)

		self.timerB = Tkinter.Button(tFrame, text="Start Timed Randomize", command=start_stop_timer)
		self.timerB.grid(row=0, column=2, padx=10)





		#MacAddress Set frame
		def setMac():
			text = self.macT1.get() + ":" + self.macT2.get() + ":" + self.macT3.get() + ":" + self.macT4.get() + ":" + self.macT5.get() + ":" + self.macT6.get()
			macTested = mac_regx.match(text)
			if macTested is None:
				tkMessageBox.showinfo("Wrong Input","Wrong input, please use the characters from (0-9) and (a-f) in the following format:\n xx:xx:xx:xx:xx:xx")
			else:
				if self.targetDevice == '':
					tkMessageBox.showinfo("Randomize", "Please select a target above")
				else:
					spoof_mac_specific(self.targetDevice, text, self.password.get())
					refreshInfoFrame()

		macFrame = Tkinter.LabelFrame(self, padx=10, pady=10, text='Set MacAddress', bd=self.borderWidth)
		macFrame.grid(row=5, columnspan=2, sticky='ew', padx=10, pady=5)

		self.macT1 = Tkinter.StringVar()
		self.macE1 = Tkinter.Entry(macFrame, textvariable=self.macT1, width="2")
		self.macE1.grid(row=0, column=0)

		
		self.macL2 = Tkinter.Label(macFrame, text=":")
		self.macL2.grid(row=0, column=1)

		self.macT2 = Tkinter.StringVar()
		self.macE2 = Tkinter.Entry(macFrame,  width="2", textvariable=self.macT2)
		self.macE2.grid(row=0, column=2)

		self.macL3 = Tkinter.Label(macFrame, text=":")
		self.macL3.grid(row=0, column=3)

		self.macT3 = Tkinter.StringVar()
		self.macE3 = Tkinter.Entry(macFrame, width="2", textvariable=self.macT3)
		self.macE3.grid(row=0, column=4)

		self.macL4 = Tkinter.Label(macFrame, text=":")
		self.macL4.grid(row=0, column=5)

		self.macT4 = Tkinter.StringVar()
		self.macE4 = Tkinter.Entry(macFrame, width="2", textvariable=self.macT4)
		self.macE4.grid(row=0, column=6)

		self.macL5 = Tkinter.Label(macFrame, text=":")
		self.macL5.grid(row=0, column=7)

		self.macT5 = Tkinter.StringVar()
		self.macE5 = Tkinter.Entry(macFrame, width="2", textvariable=self.macT5)
		self.macE5.grid(row=0, column=8)

		self.macL6 = Tkinter.Label(macFrame, text=":")
		self.macL6.grid(row=0, column=9)

		self.macT6 = Tkinter.StringVar()
		self.macE6 = Tkinter.Entry(macFrame, width="2", textvariable=self.macT6)
		self.macE6.grid(row=0, column=10)

		self.macL7 = Tkinter.Label(macFrame, text="    ")
		self.macL7.grid(row=0, column=11)

		self.macB1 = Tkinter.Button(macFrame, text="Set MacAddress", command=setMac, width=16)
		self.macB1.grid(row=0, column=12, padx=10, sticky="E")


		saveData(self.targetOriginalMac)




		#Log Frame
		logFrame = Tkinter.LabelFrame(self, text=self.target + ' log', bd=self.borderWidth)
		logFrame.grid(row=6, columnspan=2, sticky='ew', padx=10, pady=5)

		logList = Tkinter.Text(logFrame, height=10, width=60)
		logList.grid(sticky="nsew", padx=10)

		

		def updateLog():
			if 'Wi-Fi' in self.target:
				logList.delete(1.0, 'end')
				with open('log.json') as data_file:
					dataFile = json.load(data_file)
					pos = 1.0
					for entry in dataFile:
						logList.insert(pos, entry['YourFuckingISP'])
						pos = pos + 1.0
						logList.insert(pos, '\n    Connections: ')
						pos = pos + 1.0
						for con in entry['Connections']:
							logList.insert(pos, '\n        ' + con['Time Stamp'] + ' - ' + con['MacAddress'])
							pos = pos + 1.0
			else:
				logList.delete(1.0, 'end')
				logList.insert(1.0, 'No data')
		refreshInfoFrameExtra()
		updateLog()

		







#turn off network card
def disconnect(device, password):
	ps = subprocess.Popen(('echo', password), stdout=subprocess.PIPE)
	output = subprocess.check_output(('sudo', '-S', 'ifconfig', device, 'down'), stdin=ps.stdout)
	ps.wait()
	
#turn network card back on
def connect(device, password):	
	ps = subprocess.Popen(('echo', password), stdout=subprocess.PIPE)
	output = subprocess.check_output(('sudo', '-S', 'ifconfig', device, 'up'), stdin=ps.stdout)
	ps.wait()

#generate random mac address
def randomize():
	
	random_mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	random_mac= ':'.join(map(lambda x: "%02x" % x, random_mac))
	return random_mac


#set random mac address
def spoof_mac_random(device, password):
	
	macAddress = randomize()

	#set new mac address
	try:
		ps = subprocess.Popen(('echo', password), stdout=subprocess.PIPE)
		output = subprocess.check_output(('sudo', '-S', 'ifconfig', device, 'ether', macAddress), stdin=ps.stdout)
		ps.wait()
	except subprocess.CalledProcessError:
		tkMessageBox.showinfo("Missing permission", "Please enter your password")
	
	#turn off wifi to disconnect from network
	disconnect(device, password)
	#turn on wifi to automatically reconnect to the network with new mac address
	connect(device, password)


	t = threading.Timer(10.0, lambda: saveData(macAddress))
	t.start()

#set specific mac address of your choosing
def spoof_mac_specific(device,mac,password):

	#set new mac address
	try:
		ps = subprocess.Popen(('echo', password), stdout=subprocess.PIPE)
		output = subprocess.check_output(('sudo', '-S', 'ifconfig', device, 'ether', mac), stdin=ps.stdout)
		ps.wait()
	except subprocess.CalledProcessError:
		tkMessageBox.showinfo("Missing permission", "Please enter your password")
	
	#turn off wifi to disconnect from network
	disconnect(device, password)
	#turn on wifi to automatically reconnect to the network with new mac address
	connect(device, password)

	t = threading.Timer(10.0, lambda: saveData(mac))
	t.start()

#save data
def saveData(mac):
	url = "https://wtfismyip.com/json"
	response = urllib.urlopen(url)
	initialData = response.read()
	if "Unavailable" in initialData:
		print "Error"
	else:
		data = json.loads(initialData)

		localtime = time.asctime( time.localtime(time.time()))
		if os.path.isfile('log.json'):
			with open('log.json') as data_file:
				dataFile = json.load(data_file)
			counter=0
			notFound = True;
			for entry in dataFile:
				if entry['YourFuckingISP'] == data['YourFuckingISP']:
					dataFile[counter]['Connections'].append({'Time Stamp': localtime, 'MacAddress':mac})
					notFound = False;
			if notFound:
				data['Connections'] = []
				data['Connections'].append({'Time Stamp': localtime, 'MacAddress':mac})
				dataFile.append(data)
			counter = counter + 1
			with open('log.json', 'w') as outfile:
				json.dump(dataFile, outfile, indent=4)
		else:
			data['Connections'] = []
			data['Connections'].append({'Time Stamp': localtime, 'MacAddress':mac})
			outPutData = [data]
			with open('log.json', 'w') as outfile:
				json.dump(outPutData, outfile, indent=4)

	
	



		
#Format of Mac
mac_regx = re.compile(r'^([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})$', re.IGNORECASE)



if __name__ == "__main__":
	app = spoofGUI(None)
	app.title('MacSpoofer')
	app.mainloop()