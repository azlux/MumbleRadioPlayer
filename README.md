# MumbleRadioPlayer
A **DEPRECATED** Mumble bot that plays radio stream by URL

# I've merge multiple project into [botamusique](https://github.com/azlux/botamusique)
## I will not update MumbleRadioPlayer ANYMORE

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
./mumbleRadioPlayer.py --server <server_url> --user <bot_name>
`

Optional parameters :
`
--channel <default_channel>
--port <port_number>
--password <password>
--cert <certificate>
`

It's in Python 3 (The python2 version is into another branch. depreciated version !)

#### Commands
You can change commands into the configuration file, The default is :
- !play
   - from a list of url (name you have add into the configuration file)
   - with a url
- !playfile (play a file from the path into the config file)
- !list (list all files into the path of !playfile)
- !stop
- !joinme (join the user who speak to me)
- !kill
- !oust (stop + go into the default channel)
- !v <number> (change volume with a percentage )
- !np (get the current music title - now playing feature)

#### Installation
1. You need python 3 with opuslib and protobuf (look at the requirement of pymumble)
you will need pip3 (apt-get install python3-pip)
2. The Bot use ffmpeg, so you know what you have to do if ffmpeg aren't in your package manager. I personally use [this repository](http://repozytorium.mati75.eu/) on my raspberry.

commands (don't forget the sudo mode):
```
apt-get install ffmpeg
git clone --recurse-submodules https://github.com/azlux/MumbleRadioPlayer.git
cd ./MumbleRadioPlayer
pip3 install -r requirements.txt
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
When I upgarde pymumble, the requirement can change. Reinstall the pip3 requirement if you are not sure.

The bot change is own comment with the stream name. Now working with:
- ShoutCast
- IceCast

#### TODO
- [x] Make the bot speak in the channel
- [x] Better comment use (and add !help)
- [x] Option to use a certificate

=====
### Credits
Pymumble comes from [here](https://github.com/azlux/pymumble). It's, for now, the current fork alive of pymumble in PYTHON 3 now \o/
