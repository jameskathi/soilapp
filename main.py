import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import socket
import time
import re


def getdata(ip_addr): 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
	msg = "<SR><CMD><QUERY>DATA</QUERY></CMD></SR>"
	try:
		s.connect((ip_addr, 1526))
		msg = msg+'\r'
		msg = msg+'\n'
		i =1
		while i<6:
			s.sendall(msg.encode())
			dat = s.recv(1024)
			dat = dat.decode("utf-8")
			try:
				co2 = re.search("<CPRIME>(.*?)</CPRIME>", dat).group(1)
				co2 = "{:.3f}".format(float(co2))
				h2o = re.search("<H2O>(.*?)</H2O>", dat).group(1)
				h2o = "{:.3f}".format(float(h2o))
				tcham = re.search("<CHAMBERTEMP>(.*?)</CHAMBERTEMP>", dat).group(1)
				tcham = "{:.3f}".format(float(tcham))
				press = re.search("<BENCHPRESSURE>(.*?)</BENCHPRESSURE>", dat).group(1)
				press = "{:.3f}".format(float(press))
				tcell = re.search("<BENCHTEMP>(.*?)</BENCHTEMP>", dat).group(1)
				tcell = "{:.3f}".format(float(tcell))
				y = 'CO2 = '+co2+' ppm'+'\n'+'H2O = '+h2o+' mmol/mol'+'\n'+'Cell Pressure = ' \
					+press+' kPa'+'\n'+'Cell Temperature = '+tcell+' °C'+'\n'+'Chamber Temp = '+tcham+' °C'
				i=7
			except:
				print ("No Success")
				print("Trying Again")
				i +=1
				time.sleep(1)
			if i==6:
				print("Command Not Successful..exiting") 
				y = "Command not successful"
	except socket.error:
		print("Not able to connect to 8100A") 
		y = "Socket error - not able to connect to 8100A"
		s.close()	
	return y

def getsumm(ip_addr): 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
	msg = "<SR><CMD><QUERY>SUMMARY</QUERY></CMD></SR>"
	try:
		s.connect((ip_addr, 1526))
		msg = msg+'\r'
		msg = msg+'\n'
		i =1
		while i<6:
			s.sendall(msg.encode())
			dat = s.recv(1024)
			dat = dat.decode("utf-8")
			try:
				expf = re.search("<EXPFLUX>(.*?)</EXPFLUX>", dat).group(1)
				expf = "{:.3f}".format(float(expf))
				expcv = re.search("<EXPFLUXCV>(.*?)</EXPFLUXCV>", dat).group(1)
				expcv = "{:.3f}".format(float(expcv))
				
				y = 'Exponential Flux = '+expf+' umolm^2s^-1 '+'\n'+'Flux CV = '+expcv
				i=7
			except:
				print ("No Success")
				print("Trying Again")
				i +=1
				time.sleep(1)
			if i==6:
				print("Command Not Successful..exiting") 
				y = "Command not successful"
	except socket.error:
		print("Not able to connect to 8100A") 
		y = "Socket error - not able to connect to 8100A"
		s.close()	
	return y


def set8100msg(ip_addr,msg):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
	
	try:
		s.connect((ip_addr, 1526))
		msg = msg+'\r'
		msg = msg+'\n'
		i =1
		while i<6:
			s.sendall(msg.encode())
			ack = s.recv(1024)
			ack = ack.decode("utf-8")
			print(ack)
			if ack.find("<SR><ACK>TRUE</ACK></SR>") is not -1:
				print("Success")
				i=7
				y = "Success"
			else:
				print ("No Success")
				print("Trying Again")
			i +=1
			time.sleep(2)
			if i==6:
				print("Command Not Successful..exiting") 
				y = "Command not successful"
	except socket.error:
		print("Not able to connect to 8100A") 
		y = "Socket error - not able to connect to 8100A"
		s.close()	
	return y



class MyGridLayout(GridLayout):
	# Initialize infinite keywords
	def __init__(self, **kwargs):
		# Call grid layout constructor
		super(MyGridLayout, self).__init__(**kwargs)
		# Set columns
		self.cols = 2

		# Add widgets
		label1 = Label(text="IP Address: ",font_size=28) 
		self.add_widget(label1)

		# Add Input Box
		self.ipaddress = TextInput(text='',halign="center",multiline=False,font_size=30)
		self.add_widget(self.ipaddress)

    

		
		self.add_widget(Label(text="Enter Collar: ",font_size=28))
		# Add Input Box
		self.collar = TextInput(text='',halign="center",multiline=False,font_size=30)
		self.add_widget(self.collar)
		label2 = Label(text="Enter Label: ",font_size=28)
		self.add_widget(label2)
		# Add Input Box
		self.lbl = TextInput(text='',halign="center",multiline=False,font_size=30)
		self.add_widget(self.lbl)

        # Create a set collar ht Button
		self.collarst = Button(text="Set Collar Height (cm)", font_size=32)
		# Bind the button
		self.collarst.bind(on_press=self.setcollar)
		self.add_widget(self.collarst)

		# Create a connect Button
		self.startb = Button(text="Start", font_size=32)
		# Bind the button
		self.startb.bind(on_press=self.startm)
		self.add_widget(self.startb)

# Create a connect Button
		self.stopb = Button(text="Stop", font_size=32)
		# Bind the button
		self.stopb.bind(on_press=self.stopm)
		self.add_widget(self.stopb)

		self.snapb = Button(text="Snap Shot", font_size=32)
		# Bind the button
		self.snapb.bind(on_press=self.getsnapshot)
		self.add_widget(self.snapb)

		self.sumb = Button(text="Summary", font_size=32)
		self.sumb.bind(on_press=self.getsummary)
		self.add_widget(self.sumb)

		self.status = Label(text="----",font_size=15)
		self.add_widget(self.status)

	def setcollar(self,instance):
		self.status.text = "Setting collar height..please wait"
		clht = str(float(self.collar.text))
		lbl  = str(self.lbl.text)
		if len(lbl) == 0:
			lbl = "NONE"
		
		ip_addr_81A = self.ipaddress.text
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>"
		try:
			set8100msg(ip_addr_81A,msg1)
		except:
			pass
	
		msg2 = "<SR><PORT><CHAMBER><COLLARHEIGHT>"+clht+"</COLLARHEIGHT></CHAMBER><OBSERVATION><LABEL>"+lbl+\
			"</LABEL></OBSERVATION></PORT></SR>"
		#msg3 = "<SR><CFG><IPOUTRATE>1</IPOUTRATE></CFG></SR>" 
		y = set8100msg(ip_addr_81A,msg2)
		self.status.text = "Collar height update = " + y
		#set8100msg(ip_addr_81A,msg3)

	def startm(self,instance):
		self.status.text = "Starting measurement..please wait"
		ip_addr_81A = self.ipaddress.text
		msg2 = "<SR><CMD><MEAS>START</MEAS></CMD></SR>"
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>" 
		#msg3 = "<SR><CFG><IPOUTRATE>1</IPOUTRATE></CFG></SR>" 
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>"
		try:
			set8100msg(ip_addr_81A,msg1)
		except:
			pass
		y = set8100msg(ip_addr_81A,msg2)
		#set8100msg(ip_addr_81A,msg3)
		self.status.text = "Measurement start status = " + y

	def getsnapshot(self, instance):
		self.status.text = "Getting snap shot..please wait"
		ip_addr_81A = self.ipaddress.text
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>" 
		try:
			set8100msg(ip_addr_81A,msg1)
		except:
			pass
		y = getdata(ip_addr_81A)
		self.status.text = y

	def getsummary(self, instance):
		self.status.text = "Getting Summary..please wait"
		ip_addr_81A = self.ipaddress.text
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>" 
		try:
			set8100msg(ip_addr_81A,msg1)
		except:
			pass
		y = getsumm(ip_addr_81A)
		self.status.text = y




	def stopm(self,instance):
		self.status.text = "Stopping measurement..please wait"
		ip_addr_81A = self.ipaddress.text
		msg2 = "<SR><CMD><MEAS>STOP</MEAS></CMD></SR>"
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>" 
		#msg3 = "<SR><CFG><IPOUTRATE>1</IPOUTRATE></CFG></SR>" 
		msg1 = "<SR><CFG><IPOUTRATE>0</IPOUTRATE></CFG></SR>"
		try:
			set8100msg(ip_addr_81A,msg1)
		except:
			pass
		y = set8100msg(ip_addr_81A,msg2)
		#set8100msg(ip_addr_81A,msg3)
		self.status.text = "Measurement stop status = " + y

    


class SoilApp(App):
	def build(self):
		return MyGridLayout()




if __name__ == '__main__':
	SoilApp().run()
