# MumbleRadioPlayer
A Mumble bot that plays radio stream by URL

======

1. [How to start the bot](#how-to-start-the-bot)
2. [Commands](#commands)
3. [Installation](#installation)
4. [Important](#important)
5. [How to help](#how-to-help)
6. [Additionnal informations](#additionnal-informations)
7. [TODO](#todo)
8. [Credits](#credits)

#### How to start the bot
Run the mumbleRadioPlayer.py to start the bot (don't forget the `chmod +x ./mumbleRadioPlayer.py`)
`
./mumbleRadioPlayer.py -server <server_url> -user <bot_name>
`

Optional parameters :
`
-channel <default_channel>
-port <port_number>
-password <password>
`

It's in Python 2

#### Commands
You can change commands into the configuration file, The default is :
- !play
   - from a list of url (name you have add into the configuration file)
   - with a url
- !stop
- !joinme (join the user who speak to me)
- !kill
- !oust (stop + go into the default channel)
- !v <number> (change volume with a percentage )
- !np (get the current music title - now playing feature)

#### Installation
1. You need python 2 with opuslib and protobuf (look at the requirement of pymumble)
2. The Bot use ffmpeg, so you know what you have to do if ffmpeg aren't in your package manager. I personally use [this repository](http://repozytorium.mati75.eu/) on my raspberry.

commands (don't forget the sudo mode):
```
pip install opuslib
pip install protobuf
apt-get install ffmpeg
git clone https://github.com/azlux/MumbleRadioPlayer.git
cd ./MumbleRadioPlayer
chmod +x ./mumbleRadioPlayer.py
```


If you really want to install pymumble independently, there are a install.sh. But think about upgrade. The Bot will work that way too.

#### Important
What the bot cannot do:

1. A .pls file is **NOT** a stream url, it's just a text file. Take a look inside if you can found real stream url. A good url can be read by your browser natively.
2. The configuration file is **NOT** UTF-8 encoded, be careful
#### How to help
Because, Yes, You can help.
- If you find bugs, problems, errors, mistakes, you can create an issue on github.
- If you have a suggestion or want a new feature, you can create an issue.
- If you want to make change by your own, fork and pull. We will discuss about your code.


#### Additionnal informations
If a command doesn't work, try to find the error, or send me the command and I will try to reproduce it.

The bot change is own comment with the stream name. Now working with:
- ShoutCast
- IceCast

#### TODO
- [x] Make the bot speak in the channel
- [ ] Option to use a certificate

=====
### Credits
Pymumble comes from [here](https://github.com/azlux/pymumble), it's a fork of [Xefir's fork](https://github.com/Xefir/pymumble), It's, for now, the current fork alive of pymumble
