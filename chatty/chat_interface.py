#!/usr/bin/env python
import sys, pygtk, gtk, xml.dom.minidom, os, string, re, dbus, gobject, time, pynotify, StringIO, datetime
# import crazy_world, nil, nothing, seriously?
from xml.dom.minidom import parse
from dbus.mainloop.glib import DBusGMainLoop
from datetime import date

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
  

settingssource = """<?xml version="1.0"?>
<chattd>
<options updated="initial">
	<enabled type="disabled" enabled="now" time="30" />
	<actions>
		<popup enabled="False"/>
		<respond enabled="False"/>
		<log enabled="False"/>
		<autoreply enabled="True"/>
	</actions>
	<autoengine>
		<replace trigger="hi" replace="Hey!" />
		<replace trigger="go school" replace="I'm Homeschooled. You?" />
		<replace trigger="bye" replace="Bye, talk to you later!" />
		<replace trigger="like hobbies" replace="Hmm... Take a look at http://iain.in/" />
	</autoengine>
	<chatback>I'm Sorry, but Iain isn't able to answer the computer right now.
I've been here idle for about $time mins.</chatback>
	<notification>
		$name chatted you at $time with the message, '$msg'.
	</notification>
</options>
<chats>
	<person name="TesterZ">
		<chat time="1257465989">Does this work?</chat>
		<chat time="1257465989">Awesome!</chat>
	</person>
</chats>
</chattd>
"""

class PidginBus:

	def __init__(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()
		self.obj = self.bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
		self.gs  = self.bus.get_object('org.gnome.ScreenSaver','/org/gnome/ScreenSaver')
		self.purple = dbus.Interface(self.obj, "im.pidgin.purple.PurpleInterface")
		self.chattd = []
		self.bus.add_signal_receiver(self.msg_recieved,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="ReceivedImMsg")
                pynotify.init('Chattd')

	def msg_recieved(self,account, sender, message, conversation, flags):
	    if re.match(r'<|>', message):
	    	message = re.sub(r'<(.|\n)*?>','',message)
	    name = self.purple.PurpleConversationGetTitle(conversation)
    	    idletime = int(self.gs.GetSessionIdleTime() / 60)
    
    	    if ((datastore.getEnabled() == 'now') or ((datastore.getEnabled() == 'idle') and (self.gs.GetSessionIdleTime() > datastore.idleTime))):
	    	if sender not in self.chattd:
	    		notifymessage = self.parse(datastore.chatback(), idletime, name, message)
	    		notification = self.parse(datastore.notification(), idletime, name, message)
	    		time.sleep(2)
	    		self.purple.PurpleConvImSend(self.purple.PurpleConvIm(conversation), notifymessage);
	    		self.notify(notification)
	    		self.chattd.append(str(sender))
	    datastore.addChat(message,name)

	def notify(self,text):
		alert = pynotify.Notification(text)
		alert.set_urgency(pynotify.URGENCY_NORMAL)
		alert.set_timeout(pynotify.EXPIRES_NEVER)
		alert.set_hint('x', (150 * ((len(self.chattd) // 10) + 1)))
		alert.set_hint('y', (120 * (len(self.chattd) % 10) ))
		alert.show()

	def parse(self, template, idletime, name, message):
		tpl = string.Template(template)
		out = tpl.safe_substitute(msg = message[:50],
					  message = message,
					  name = name,
					  idle = idletime,
					  idle = idletime,
					  time = time.strftime('%H:%M')
					 )
		return out

class DataStore:
	
	def __init__(self):
		self.location = 'data.chatty'
		if (not os.path.exists(self.location) or (os.path.getsize(self.location) < 5)):
			file = open(self.location, 'w')
			file.writelines(settingssource)
			file.close()
		self.parser = xml.dom.minidom.getDOMImplementation()
		self.xml = parse(self.location)
	
	def __del__(self):
		self.saveData()
		
	def saveData(self):
		xmlfile = self.xml.toxml()
		if xmlfile:
			file = open(self.location,'w')
			file.writelines(xmlfile)
			file.close()
			print 'Datastore saved and closed'	
	
	def notification(self,set = False):
		if set:
			self.xml.getElementsByTagName('notification')[0].firstChild.nodeValue = set
		return self.xml.getElementsByTagName('notification')[0].firstChild.nodeValue
		
	def chatback(self,set = False):
		if set:
			self.xml.getElementsByTagName('chatback')[0].firstChild.nodeValue = set
		return self.xml.getElementsByTagName('chatback')[0].firstChild.nodeValue

	def setEnabled(self,value):
		return self.xml.getElementsByTagName('enabled')[0].setAttribute("enabled", value)
	
	def getEnabled(self):
		return self.xml.getElementsByTagName('enabled')[0].getAttribute("enabled")
	
	def clearHistory(self):
		self.xml.getElementsByTagName('chats').nodeValue = None
	
	def idleTime(self, value):
		idletime = self.xml.getElementsByTagName('enabled')[0]
		if value:	
			idletime.setAttribute('time', value)
		return idletime.getAttribute('time')
	
	def addChat(self, text, fromUser):
		selected_person = False
		for person in self.xml.getElementsByTagName('person'):
			if (person.getAttribute('name') == fromUser):
				selected_person = person

		if selected_person == False:
			new_person = self.xml.createElement('person')
			new_person.setAttribute('name',fromUser)
			selected_person = self.xml.getElementsByTagName('chats')[0].appendChild(new_person)

		newchat_msg = self.xml.createTextNode(text)
		newchat = self.xml.createElement('chat')
		newchat.appendChild(newchat_msg)
		newchat.setAttribute('time', str(time.time()))
		selected_person.appendChild(newchat)
		#print 'saved'
		return True
	

	def clearHistory(self):
		self.xml.getElementsByTagName('')
	
	def getChats(self, treestore):
		for person in self.xml.getElementsByTagName('person'):
			root_chats = treestore.append(None, [person.getAttribute('name'),'']) 
			for chat in person.getElementsByTagName('chat'):
				new_date = time.gmtime(float(chat.getAttribute('time')))
				chat_text = chat.firstChild.nodeValue
				treestore.append(root_chats, [chat_text, time.strftime('%I:%M%P %a. %b %d', new_date)])
			
			
		
	

class Chatty:
	def disable(self,type = False):
		datastore.setEnabled(type)
		
	def enable(self,type = False):
		datastore.setEnabled(type)
		
	def autoRespond(self,type = False):
		if type:
			print 'Enabling AutoRespond'
		else:
			print 'Disabling AutoRespond'
			
class Interface:

	#Fat Skeletons
	
	def on_clear_history(self,widget):
		datastore.clearHistory()
			
	def __init__(self):
		self.main = gtk.Builder()
    		self.main.add_from_file("idled.ui") 
    		self.window = self.main.get_object("mainWindow")
     		self.main.connect_signals(self)
     		self.enable = True #Prevents Double-Checking Boxes
     		self.__setInitialValues()

     	def __setInitialValues(self):
     		self.main.get_object(datastore.getEnabled()).set_active(True)
     		buffernotify = gtk.TextBuffer()
     		buffernotify.set_text(datastore.notification())
     		self.main.get_object('alertballoontext').set_buffer(buffernotify)
     		bufferchatback = gtk.TextBuffer()
     		bufferchatback.set_text(datastore.chatback())
     		self.main.get_object('chatbacktxt').set_buffer(bufferchatback)

     	def on_chatback_update(self,widget,data= None):
     		buff = widget.get_buffer()
     		datastore.chatback(buff.get_text(buff.get_start_iter(), buff.get_end_iter()))

	def on_notify_update(self,widget,data= None):
     		buff = widget.get_buffer()
     		datastore.notification(buff.get_text(buff.get_start_iter(), buff.get_end_iter()))

	def on_clear_history(self,widget):
		datastore.clearHistory()

     	def on_chatInit(self,widget,data= None):
     		treestore = gtk.TreeStore(str, str) # Name, Time
     		treeview = self.main.get_object("allChats")
     		if treeview.get_columns():
     			for column in treeview.get_columns():
     				treeview.remove_column(column)
     		treeview.set_model(treestore)
     		chat = gtk.TreeViewColumn('Chat')
     		time = gtk.TreeViewColumn('Time')
     		chat.set_resizable(True)
     		time.set_resizable(True)
     		treeview.append_column(chat)
     		treeview.append_column(time)
     		name = date = gtk.CellRendererText()
		chat.pack_start(name, True)
		chat.add_attribute(name, "text", 0)
		time.pack_end(date, True)
     		time.add_attribute(date, "text", 1)
     		
     		datastore.getChats(treestore)
     		
     		#chat =  treestore.append(None, ['Charlie Matthews', ''])
     		#chat0 = treestore.append(chat, ['Heyy....','15:25'])
     		#chat1 = treestore.append(chat, ['wasup?','15:55'])
     		#chat2 = treestore.append(chat, ['you there?','16:54'])
	
	def on_autoEngineInit(self,widget):
		pass
	
	def goto_tabAutoengine(self,widget):
		notebook = self.main.get_object("mainnotebook")
		notebook.set_current_page(3)
	
	def on_settingsSave(self, widget):
		print 'Saved'
	
	def on_window_destroy(self, widget):
        	gtk.main_quit()
	
	def on_settingsSave(self, widget):
		print 'Saving...'
		
	def on_clearData(self, widget):
		print 'Clearing Chats...'

	def on_idle_value(self,widget):
		datastore.idleTime(widget.get_value_as_int())
	
	#Big ToggleButton Functions
	
	def on_autoreply_toggle(self,widget):
		if self.enable is True: #If removed will call twice.
			if widget.get_active():
				do = True
			else:
				do = False
			chatty.autoRespond(do)
			self.enable = False
			for obj in ['autorespond2','autorespond']:
				self.main.get_object(obj).set_active(do)
			self.enable = True
			self.main.get_object('autoengineactions').set_sensitive(do)

	def on_enable_toggle(self,widget):
		if widget.get_active():
			active_widget = widget.get_name()
			if active_widget == 'idle':
				self.main.get_object("idledtime").set_sensitive(True)
			elif active_widget == 'now':
				self.main.get_object("idledtime").set_sensitive(False)
			elif active_widget == 'disabled':
				self.main.get_object("idledtime").set_sensitive(False)
			datastore.setEnabled(active_widget)
			
	def on_init_main(self,widget):
		main_radio = self.main.get_object("idle")
		for radio in ['disabled','now']:
			self.main.get_object(radio).set_group(main_radio)
		#@todo Add in preferences reader / object to pull active variable.
		main_radio.set_active(True)

	
if __name__ == "__main__":
    chatty = Chatty()
    datastore = DataStore()
    pidgin = PidginBus()
    interface = Interface()
    interface.window.show()
    gtk.main()
    
   
