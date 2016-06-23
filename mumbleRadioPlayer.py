#!/usr/bin/python

import time
import sys
import signal
import ConfigParser
import urllib2
import json
import re
import audioop
import os
import subprocess as sp

sys.path.append(os.path.join(os.path.dirname(__file__), "pymumble"))
import pymumble

class MumbleRadioPlayer:
    def __init__(self, sys_args):
        signal.signal(signal.SIGINT, self.ctrl_caught)

        self.config = ConfigParser.ConfigParser()
        self.config.read("configuration.ini")

        host = get_args('-server', sys_args)
        user = get_args('-user', sys_args, default="StreamPlayerBot")
        port = int(get_args('-port', sys_args, default=64738))
        password = get_args('-password', sys_args, default="")

        self.channel = get_args('-channel', sys_args, default="")
        self.volume = self.config.getfloat('bot', 'volume')

        self.playing = False
        self.exit = False
        self.nbexit = 0
        self.thread = None

        self.mumble = pymumble.Mumble(host, user=user, port=port, password=password,
                                      debug=self.config.getboolean('debug', 'mumbleConnection'))
        self.mumble.callbacks.set_callback("text_received", self.message_received)

        self.mumble.start()  # start the mumble thread
        self.mumble.is_ready()  # wait for the connection
        self.set_comment()
        self.mumble.users.myself.unmute()  # by sure the user is not muted
        if self.channel:
            self.mumble.channels.find_by_name(self.channel).move_in()
        self.mumble.set_bandwidth(200000)
        self.loop()

    def ctrl_caught(self, signal, frame):
        print("\ndeconnection asked")
        self.exit = True
        self.stop()
        if self.nbexit > 2:
            print("Forced Quit")
            sys.exit(0)
        self.nbexit += 1

    def message_received(self, text):
        message = text.message
        if message[0] == '!':
            message = message[1:].split(' ', 1)

            if len(message) > 0:
                command = message[0]
                parameter = ''
                if len(message) > 1:
                    parameter = message[1]
            else:
                return

            print(command + ' - ' + parameter)
            if command == 'play' and parameter:
                self.play(parameter)

            elif command == 'stop':
                self.stop()

            elif command == 'kill':
                if self.is_admin(text.actor):
                    self.stop()
                    self.exit = True
                else:
                    print("You are not an admin")

            elif command == 'oust':
                self.stop()
                if self.channel:
                    self.mumble.channels.find_by_name(self.channel).move_in()

            elif command == 'joinme':
                self.mumble.users.myself.move_in(self.mumble.users[text.actor]['channel_id'])

            elif command == 'v':
                if parameter != None and parameter.replace('.', '', 1).isdigit() and float(parameter) >= 0.0 and float(parameter) <= 1.0:
                    print("changement de volume")
                    self.volume = float(parameter)
            else:
                print("Bad command")

    def is_admin(self, user):
        # this lonnng conversion because in python2 configparser don't accept unicode
        # so i remove unicode caracter of the username
        username = self.mumble.users[user]['name'].encode('ascii', errors='ignore').strip()
        list_admin = self.config.get('bot', 'admin').split(';')
        if username in list_admin:
            return True
        else:
            return False

    def play(self, msg):
        if self.config.has_option('stream', msg):
            url = self.config.get('stream', msg)
            self.launch_play(url)
        elif self.config.getboolean('bot', 'allow_new_url') and get_url(msg):
            self.launch_play(get_url(msg))
        else:
            print("Bad input")

    def launch_play(self, url):
        info = get_server_description(url)
        if info != False:
            self.stop()

            time.sleep(2)
            if self.config.getboolean('debug', 'ffmpeg'):
                ffmpeg_debug = "debug"
            else:
                ffmpeg_debug = "warning"
            command = ["ffmpeg", '-v', ffmpeg_debug, '-nostdin', '-i', url, '-ac', '1', '-f', 's16le', '-ar', '48000', '-']
            print(command)
            self.set_comment("Stream from %s" % info)
            time.sleep(3)
            self.playing = True

    def loop(self):
        while not self.exit:
            if self.playing:
                while self.mumble.sound_output.get_buffer_size() > 0.5 and self.playing:
                    time.sleep(0.01)
                self.mumble.sound_output.add_sound(audioop.mul(self.thread.stdout.read(480), 2, self.volume))
            else:
                time.sleep(1)

        while self.mumble.sound_output.get_buffer_size() > 0:
            time.sleep(0.01)
        time.sleep(0.5)

    def stop(self):
        if self.thread:
            self.playing = False
            time.sleep(0.5)
            self.thread.kill()
            self.thread = None
            print("Stop")

    def set_comment(self, txt=None):
        if txt is None:
            txt = ""
        self.mumble.users.myself.comment(txt + "<p /> " + self.config.get('bot', 'comment'))


def get_url(url):
    if url.startswith('http'):
        return url
    p = re.compile('href="(.+)"', re.IGNORECASE)
    res = re.search(p, url)
    if res:
        return res.group(1)
    else:
        return False


def get_server_description(url):
    p = re.compile('(https?\:\/\/[^\/]*)', re.IGNORECASE)
    res = re.search(p, url)
    base_url = res.group(1)
    url_icecast = base_url + '/status-json.xsl'
    url_shoutcast = base_url + '/stats?json=1'
    try:
        request = urllib2.Request(url_icecast)
        response = urllib2.urlopen(request)
        data = json.loads(response.read())
        title_server = data['icestats']['source'][0]['server_name'] + ' - ' + data['icestats']['source'][0][
            'server_description']
        if not title_server:
            request = urllib2.Request(url_shoutcast)
            response = urllib2.urlopen(request)
            data = json.loads(response.read())
            title_server = data['servertitle']
            if not title_server:
                title_server = url
    except (urllib2.Request, urllib2.urlopen):
        title_server = url
    except urllib2.HTTPError:
        return False
    return title_server


def get_title(url):
    request = urllib2.Request(url)
    try:
        request.add_header('Icy-MetaData', 1)
        response = urllib2.urlopen(request)
        icy_metaint_header = response.headers.get('icy-metaint')
        if icy_metaint_header is not None:
            metaint = int(icy_metaint_header)
            read_buffer = metaint + 255
            content = response.read(read_buffer)
            title = content[metaint:].split("'")
            print(title)
    except (urllib2.Request, urllib2.urlopen):
        print('Error')


def get_args(name, sys_args, default=None):
    if name in sys_args:
        try:
            res = str(sys_args[sys_args.index(name) + 1])
            return str(res)
        except IndexError:
            print("option of " + name + " is missing !")
            sys.exit(1)

    elif default != None:
        return default

    else:
        print("parameter " + name + " is missing !")
        sys.exit(1)


if __name__ == '__main__':
    playbot = MumbleRadioPlayer(sys.argv[1::])
