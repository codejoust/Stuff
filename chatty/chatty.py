#!/usr/bin/env python
import dbus, gobject, time, re, pynotify, dbus
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
gs = bus.get_object('org.gnome.ScreenSaver','/org/gnome/ScreenSaver')
pynotify.init('Chattd')

isIdle = False
chattd = []

def notify(sender, message):
	alert = pynotify.Notification(
			"Chat from "+sender[0:30],
			"You've been chatted by "+sender+" at "+time.strftime('%H:%M'),
			re.sub('/<.*>/','',message))
	alert.set_urgency(pynotify.URGENCY_NORMAL)
	alert.set_timeout(pynotify.EXPIRES_NEVER)
	alert.set_hint('x', (150 * ((len(chattd) // 10) + 1)))
	alert.set_hint('y', (120 * (len(chattd) % 10) ))
	alert.show()


def msg_recieved(account, sender, message, conversation, flags):
    if gs.GetSessionIdle() is 1:
    	if sender not in chattd:
    		message = "Hi, this is Iain's Computer trying to take messages.\n Iain's been gone for about " + str(gs.GetSessionIdleTime() // 60) + " mins.\n \nI'll get back to you soon, if you want, you are welcome to leave a message."
    		purple.PurpleConvImSend(purple.PurpleConvIm(conversation), message);
    		notify(purple.PurpleConversationGetTitle(conversation),message)
    		chattd.append(str(sender))

bus.add_signal_receiver(msg_recieved,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="ReceivedImMsg")

"""
def set_idle(status):
	if (status == True):
		#time.sleep(20)
		isIdle = True
		print "Idle Now"
	else:
		isIdle = False
		print "resumed"

#bus.add_signal_receiver(set_idle,
#			dbus_interface="org.gnome.ScreenSaver",
			signal_name="SessionIdleChanged")
"""

loop = gobject.MainLoop()
loop.run()
