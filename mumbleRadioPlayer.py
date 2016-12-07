#!/usr/bin/python3
import struct

import time
import sys
import signal
import configparser
import urllib.request, urllib.error, urllib.parse
import json
import re
import audioop
import subprocess as sp
import pymumble.pymumble_py3 as pymumble
import argparse
import os.path
from os import listdir


class MumbleRadioPlayer:
    def __init__(self):
        signal.signal(signal.SIGINT, self.ctrl_caught)

        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read("configuration.ini")

        parser = argparse.ArgumentParser(description='Bot for playing radio stream on Mumble')
        parser.add_argument("-s", "--server", dest="host", type=str, required=True, help="The server's hostame of a mumble server")
        parser.add_argument("-u", "--user", dest="user", type=str, required=True, help="Username you wish, Default=abot")
        parser.add_argument("-P", "--password", dest="password", type=str, default="", help="Password if server requires one")
        parser.add_argument("-p", "--port", dest="port", type=int, default=64738, help="Port for the mumble server")
        parser.add_argument("-c", "--channel", dest="channel", type=str, default="", help="Default chanel for the bot")

        args = parser.parse_args()
        self.volume = self.config.getfloat('bot', 'volume')
        self.channel = args.channel
        self.playing = False
        self.url = None
        self.exit = False
        self.nb_exit = 0
        self.thread = None

        self.mumble = pymumble.Mumble(args.host, user=args.user, port=args.port, password=args.password,
                                      debug=self.config.getboolean('debug', 'mumbleConnection'))
        self.mumble.callbacks.set_callback("text_received", self.message_received)

        self.mumble.set_codec_profile("audio")
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
        if self.nb_exit > 2:
            print("Forced Quit")
            sys.exit(0)
        self.nb_exit += 1

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

            print(command + ' - ' + parameter + ' by ' + self.mumble.users[text.actor]['name'])
            if command == self.config.get('command', 'play_stream') and parameter:
                self.play_stream(parameter)

            if command == self.config.get('command', 'play_file') and parameter:
                path = self.config.get('bot', 'music_folder') + parameter
                if "/" in parameter:
                    self.mumble.users[text.actor].send_message(self.config.get('strings', 'bad_file'))
                elif os.path.isfile(path):
                    self.launch_play_file(path)
                else:
                    self.mumble.users[text.actor].send_message(self.config.get('strings', 'bad_file'))

            elif command == self.config.get('command', 'stop'):
                self.stop()

            elif command == self.config.get('command', 'kill'):
                if self.is_admin(text.actor):
                    self.stop()
                    self.exit = True
                else:
                    self.mumble.users[text.actor].send_message(self.config.get('strings', 'not_admin'))

            elif command == self.config.get('command', 'stop_and_getout'):
                self.stop()
                if self.channel:
                    self.mumble.channels.find_by_name(self.channel).move_in()

            elif command == self.config.get('command', 'joinme'):
                self.mumble.users.myself.move_in(self.mumble.users[text.actor]['channel_id'])

            elif command == self.config.get('command', 'volume'):
                if parameter is not None and parameter.isdigit() and 0 <= int(parameter) <= 100:
                    self.volume = float(float(parameter) / 100)
                    self.send_msg_channel(self.config.get('strings', 'change_volume') % (
                        int(self.volume * 100), self.mumble.users[text.actor]['name']))
                else:
                    self.send_msg_channel(self.config.get('strings', 'current_volume') % int(self.volume * 100))

            elif command == self.config.get('command', 'current_music'):
                if self.url is not None:
                    self.send_msg_channel(get_title(self.url))
                else:
                    self.mumble.users[text.actor].send_message(self.config.get('strings', 'not_playing'))
            
            elif command == self.config.get('command', 'list'):
                folder_path = self.config.get('bot', 'music_folder')
                files = [f for f in listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                if files :
                    self.mumble.users[text.actor].send_message('<br>'.join(files))
                else :
                     self.mumble.users[text.actor].send_message(self.config.get('strings', 'no_file')) 

            else:
                self.mumble.users[text.actor].send_message(self.config.get('strings', 'bad_command'))

    def is_admin(self, user):
        username = self.mumble.users[user]['name']
        list_admin = self.config.get('bot', 'admin').split(';')
        if username in list_admin:
            return True
        else:
            return False

    def play_stream(self, msg):
        if self.config.has_option('stream', msg):
            url = self.config.get('stream', msg)
            self.launch_play_stream(url)
        elif self.config.getboolean('bot', 'allow_new_url') and get_url(msg):
            self.launch_play_stream(get_url(msg))
        else:
            print("Bad input")

    def launch_play_stream(self, url):
        info = get_server_description(url)
        if info != False:
            self.stop()

            time.sleep(2)
            if self.config.getboolean('debug', 'ffmpeg'):
                ffmpeg_debug = "debug"
            else:
                ffmpeg_debug = "warning"
            command = ["ffmpeg", '-v', ffmpeg_debug, '-nostdin', '-i', url, '-ac', '1', '-f', 's16le', '-ar', '48000', '-']

            self.url = url
            self.thread = sp.Popen(command, stdout=sp.PIPE, bufsize=480)
            self.set_comment("Stream from %s" % info)
            time.sleep(3)
            self.playing = True

    def launch_play_file(self, path):
        self.stop()
        if self.config.getboolean('debug', 'ffmpeg'):
            ffmpeg_debug = "debug"
        else:
            ffmpeg_debug = "warning"
        command = ["ffmpeg", '-v', ffmpeg_debug, '-nostdin', '-i', path, '-ac', '1', '-f', 's16le', '-ar', '48000', '-']
        self.thread = sp.Popen(command, stdout=sp.PIPE, bufsize=480)
        self.playing = True

    def loop(self):
        while not self.exit:
            if self.playing:
                while self.mumble.sound_output.get_buffer_size() > 0.5 and self.playing:
                    time.sleep(0.01)
                raw_music = self.thread.stdout.read(480)
                if raw_music:
                    self.mumble.sound_output.add_sound(audioop.mul(raw_music, 2, self.volume))
                else:
                    time.sleep(0.01)
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
            self.url = None

    def set_comment(self, txt=None):
        if txt is None:
            txt = ""
        self.mumble.users.myself.comment(txt + "<p /> " + self.config.get('bot', 'comment'))

    def send_msg_channel(self, msg, channel=None):
        if not channel:
            channel = self.mumble.channels[self.mumble.users.myself['channel_id']]
        channel.send_text_message(msg)


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
    title_server = None
    try:
        request = urllib.request.Request(url_shoutcast)
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode("utf-8"))
        title_server = data['servertitle']
    except urllib.error.HTTPError:
        pass


    except ValueError:
        return False

    if not title_server:
        try:
            request = urllib.request.Request(url_icecast)
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode("utf-8"))
            title_server = data['icestats']['source'][0]['server_name'] + ' - ' + data['icestats']['source'][0]['server_description']

            if not title_server:
                title_server = url
        except urllib.error.URLError:
            title_server = url
        except urllib.error.HTTPError:
            return False
    return title_server


def get_title(url):
    request = urllib.request.Request(url, headers={'Icy-MetaData': 1})
    try:

        response = urllib.request.urlopen(request)
        icy_metaint_header = int(response.headers['icy-metaint'])
        if icy_metaint_header is not None:
            response.read(icy_metaint_header)

            metadata_length = struct.unpack('B', response.read(1))[0] * 16  # length byte
            metadata = response.read(metadata_length).rstrip(b'\0')
            print(metadata, file=sys.stderr)
            # extract title from the metadata
            m = re.search(br"StreamTitle='([^']*)';", metadata)
            if m:
                title = m.group(1)
                if title:
                    return title
    except (urllib.error.URLError, urllib.error.HTTPError):
        pass
    return 'Impossible to get the music title'


if __name__ == '__main__':
    playbot = MumbleRadioPlayer()
