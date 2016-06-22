#!/usr/bin/python
import time
import sys
import signal
import ConfigParser
import urllib2
import json
import re
import audioop

import pymumble
import subprocess as sp


class MumblePlayUrlBot:
    def __init__(self):
        signal.signal(signal.SIGINT, self.ctrl_caught)

        self.config = ConfigParser.SafeConfigParser({'password': ''}, allow_no_value=True)
        self.config.read("configuration.ini")

        host = self.config.get('server', 'host')
        user = self.config.get('server', 'user')
        user = " StreamPlayer"
        port = self.config.getint('server', 'port')
        password = self.config.get('server', 'password')
        debug = False

        self.channel = self.config.get('server', 'channel')
        self.volume = self.config.getfloat('bot', 'volume')

        self.playing = False
        self.exit = False
        self.nbexit = 0
        self.mumble = pymumble.Mumble(host, user=user, port=port, password=password, debug=debug)
        self.mumble.callbacks.set_callback("text_received", self.message_received)

        self.mumble.start()  # start the mumble thread
        self.mumble.is_ready()  # wait for the connection
        self.set_comment()
        self.mumble.users.myself.unmute()  # by sure the user is not muted
        self.mumble.channels.find_by_name(self.channel).move_in()
        self.mumble.set_bandwidth(200000)
        self.thread = None
        self.loop()

    def ctrl_caught(self, signal, frame):
        print("\ndeconnection asked")
        self.exit = True
        if self.nbexit > 2:
            print("Forced Quit")
            sys.exit(0)
        self.nbexit += 1

    def message_received(self, texte):
        message = texte.message
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
                self.exit = True

            elif command == 'oust':
                self.stop()
                self.mumble.channels.find_by_name(self.channel).move_in()

            elif command == 'joinme':
                self.mumble.users.myself.move_in(self.mumble.users[texte.actor]['channel_id'])
            elif command == 'v':
                if parameter and parameter.replace('.', '', 1).isdigit() and parameter >= 0 and parameter <=1 :
                    print("changement de volume")
                    self.volume = float(parameter)

    def play(self, msg):
        if self.config.has_option('stream', msg):
            url = self.config.get('stream', msg)
            self.launch_play(url)
        elif get_url(msg):
            self.launch_play(get_url(msg))
        else:
            print("Bad URL")

    def launch_play(self, url):
        self.stop()

        time.sleep(2)

        command = ["ffmpeg", '-v', 'warning', '-nostdin', '-i', url, '-ac', '1', '-f', 's16le', '-ar', '48000', '-']
        print(command)
        self.thread = sp.Popen(command, stdout=sp.PIPE, bufsize=480)
        self.set_comment("Stream from %s" % get_server_description(url))
        time.sleep(3)
        self.playing = True

    def loop(self):
        while not self.exit:
            if self.playing:
                while self.mumble.sound_output.get_buffer_size() > 0.5:
                    time.sleep(0.01)

                self.mumble.sound_output.add_sound(audioop.mul(self.thread.stdout.read(480), 2, self.volume))
            else:
                time.sleep(1)

        while self.mumble.sound_output.get_buffer_size() > 0:
            time.sleep(0.01)
        time.sleep(0.5)

    def stop(self):
        if self.thread:
            self.thread.kill()
            self.playing = False
            print("Stop")

    def set_comment(self, txt=None):
        if txt is None:
            txt = ""
        self.config.get('server', 'comment')
        self.mumble.users.myself.comment(txt + "<p /> " + self.config.get('server', 'comment'))


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
    request = urllib2.Request(url_icecast)
    try:
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
    except:
        title_server = url
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
    except:
        print('Error')


if __name__ == '__main__':
    playbot = MumblePlayUrlBot()
