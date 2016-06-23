# MumbleRadioPlayer
A Mumble bot that plays radio stream by URL

![Alt progression] (http://progressed.io/bar/90)
======
Run the mumbleRadioPlayer.py to start the bot.  
It's in Python 2

####What the bot can do
commands :
- [x] !play
   - [x] from a list of url
   - [x] from a url
- [x] !stop
- [x] !joinme (join the user who speak to me)
- [x] !kill
- [x] !oust (stop + go into the default channel)
- [x] !v <number> (change volume with a percentage )

#### info
The bot can't speak as this is not implemented into pymumble yet.  
If a command doesn't work, try to find the error, or send me the command and I will try to reproduce it.

The bot change is own comment with the stream name. Now working with :
- SouthCast
- IceCast
##### TODO
- [ ] Make the bot speak in the channel

=====
### INFO
Pymumble comes from [here](https://github.com/azlux/pymumble), it's a fork of [Xefir's fork](https://github.com/Xefir/pymumble), I will update this fork and the pymumble directory every time I make changes on pymumble for MumbleRadioPlayer.  
I'm doing that because it's was too complicated to make a directory linked to the pymumble git.
