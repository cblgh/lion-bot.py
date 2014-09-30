import socket, datetime, time, sys

class IRCBot:
    def __init__(self, SERVER='chat.freenode.net', PORT=6667, 
            NAME='lion_bot', OWNER='cblgh', FILE='dict_test.txt', 
            CHANNEL='#lionchannel', BOTPASS=""):
        self.SERVER = SERVER
        self.PORT = PORT
        self.NAME = NAME
        self.OWNER = OWNER
        self.FILE = FILE
        self.CHANNEL = CHANNEL
        self.BOTPASS = BOTPASS
        self.tz_dict = {}
        
        self.IRC = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.read_tzfile(self.FILE)
        self.irc_conn()
        self.login(self.NAME)
        self.listen()
    
    def login(self, nickname, username = 'LionBot', realname = 'Ohai', hostname = 'localhost', servername = 'Server Name'):
        self.send_data("USER %s %s %s %s" % (username, hostname, servername, realname))
        self.send_data("NICK " + nickname)
        if self.BOTPASS != "":
            self.send_data("PRIVMSG NickServ :ID " + self.BOTPASS)

    def irc_conn(self):
        self.IRC.connect((self.SERVER, self.PORT))
        print "Attempting to connect to " + self.SERVER

    def send_data(self, command):
        self.IRC.send(command + '\n')

    def send_msg(self, recipient, msg):
        self.send_data("PRIVMSG {recipient} :{msg}".format(recipient=recipient,
            msg=msg))

    def quit(self, active_channel):
        self.send_msg(active_channel, "Ciao {}!".format(active_channel))
        self.send_data('QUIT')

    def part(self, channel):
        self.send_data('PART ' + channel)

    def join_channel(self, channel):
        self.send_data("JOIN %s" % channel)

    def commands(self, send_to): #lists commands
        self.send_data("PRIVMSG " + send_to + " :@help - Displays self screen.")
        self.send_data("PRIVMSG " + send_to + " :@datetime - Returns current date and time.")
        self.send_data("PRIVMSG " + send_to + " :@stats - Displays bot statistics.")
        self.send_data("PRIVMSG " + send_to + " :SORRY ONLY @help ACTUALLY WORKS ATM EHEHEH")
    
    def add_tz(self, user, offset):
        self.tz_dict[user] = datetime.timedelta(hours=offset)

        # Iterates over a file with all the users and their utc offsets
    def read_tzfile(self, file):
        print "Attempting to read UTC offset file..."
        try:
            with open(file, 'r') as f:
                for line in f:
                    data = line.split()
                    self.tz_dict[data[0]] = datetime.timedelta(seconds=int(data[1]))
            print "Successfully read file!"
        except IOError:
            print "File not found! Proceeding without loading offset info."

    def save_tzfile(self, file):
        print "Attempting to save UTC offsets..."
        try:
            f = open(file, 'w')
            for usr, offset in self.tz_dict.iteritems():
                f.write(usr + " " + str(offset.seconds) + "\n")
            f.close()
            print "Successfully saved file!"
        except IOError:
            print "File not found!"
    
    def dance(self, channel):
        self.send_msg(channel, "\o-")
        self.send_msg(channel, "\o/")
        self.send_msg(channel, "~o~")

#todo: put all bot commands in bot_commands dict, mapping key word to function
    def listen(self):
        # irc listening loop
        while True:
            data = self.IRC.recv(4096)
            msg = data.split()
            # get the sender from the irc message
            sender = msg[0].split("!")[0].replace(":", "")
            # respond to ping so we don't timeout
            if msg[0] == 'PING':
                self.send_data("PONG {}".format(msg[1]))
            if msg[1] == 'PRIVMSG':
                active_channel = msg[2]
                # bot maker is sending me commands OBEY
                if sender == self.OWNER:
                    # data.find(string) != -1 == if we find string
                    if data.find('@invite') != -1: 
                        self.join_channel(msg[-1])
                    elif data.find('@leave') != -1:
                        self.part(active_channel)
                    elif data.find('@quit') != -1:
                        self.quit(active_channel)
                        break
                if data.find('@help') != -1:
                    print sender + " requested help."
                    self.commands(sender)
                # uh, timezone command thing -- to store timezones for people i guess
                if data.find('@tz') != -1:
                    # only owner may add timezones
                    if data.find('add') != -1 and sender == self.OWNER: 
                        # takes user, and utc offset
                        self.add_tz(msg[-2], int(msg[-1]))
                        self.save_tzfile(self.FILE)
                        self.send_msg(active_channel, "Added {}!".format(msg[-2]))
                    if data.find('all') != -1:
                        for usr, offset in self.tz_dict.iteritems():
                            self.send_msg(active_channel, usr + ': ' + str(datetime.datetime.utcnow() + offset))
                if data.find('@dance') != -1:
                    self.dance(active_channel)
                if data.find('hi' + self.NAME) != -1:
                    self.send_msg(active_channel, "o/")
            if data.find('KICK') != -1:
                self.send_data('JOIN ' + self.CHANNEL)
            print data
bot = IRCBot()
