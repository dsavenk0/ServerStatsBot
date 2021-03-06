# Server Manager Bot

A Telegram Bot:

* Commands
    * `/stats` - gives summed statistics about memory \ disk \ processes (will improve)
    * `/disk` - information about all connected units
    * `/ip` - shows your external IP address
    * `/lan` - scans all devices connected to the local network
    * `/temperatura` - shows information on the temperature of the CPU
    * `/shell` - goes into the mode of executing shell commands & sends you the output
    * `/speedtest` - broadband speed analysis tool
    * `/setmem` - set memory threshold (%) to monitor and notify if memory usage goes above it
    * `/setpoll` - set polling interval in seconds (higher than 10)
    * `/memgraph` - plots a graph of memory usage for a past period and sends you a picture of the graph
* Monitors memory usage and if it reaches above the set threshold = sends you warning message


Example summary: [Gif](http://i.imgur.com/AhCvy9W.gifv)

![Bot](http://i.imgur.com/hXT0drx.png)


Example shell command output as a message from the bot: 

![Shell](https://i.imgur.com/PtvcaSD.png)


Example graph sent by bot: [Gif](http://i.imgur.com/anX7rJR.gifv)

![Graph](http://i.imgur.com/K8mG3aM.jpg?1)

![](https://telegra.ph/file/27c225ccbb5034e33e25f.png)
# Usage

## Requirements 

* Python 3+
* [Telepot](https://github.com/nickoala/telepot)
* [Psutil](https://github.com/giampaolo/psutil) and other dependencies
    * Make sure to install it for Python 3+
    * In order to make sure that `pip` installs packages for the 3+ version:
        * `curl -O https://bootstrap.pypa.io/get-pip.py`
        * `sudo python3 get-pip.py`
        * After that `pip3 install psutil matplotlib netaddr fastcli telepot nmap`
        * Also Stackoverflow question about that [here](http://stackoverflow.com/questions/11268501/how-to-use-pip-with-python-3-x-alongside-python-2-x)
* [Matplotlib](http://matplotlib.org/) and other dependencies
    * `sudo apt-get install python3-matplotlib wget curl nmap`
* Bot key & `tokens.py`
    * Hide all the keys and admin variables in `tokens.py`. Use it only for sensitive variables. Avoid creating functions not to clutter the namespaces through the import.
    * Get a key from the [Bot Father](https://telegram.me/BotFather)
    * Get your id from the [ChatId Bot](https://telegram.me/GiveChatId_Bot)
    * Clone that repo
    * In the folder with the cloned repo create a file `tokens.py`
       * It's added to the `.gitignore` so you don't commit your own (and I don't commit mine:)
    * In that file put a string variable `telegrambot` which equals your key
       * For example: `telegrambot = "000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"`
   
## Running the bot

`python3 servstatsbot.py`

## Running the bot as "daemon"

* See included file in the repo: `servstatsbot.conf`
    * Open it and edit the path as mentiond in the comments there
* Place that file in `/etc/init/`
* Start the "daemon" with: `start servstatsbot`
    * You can start|stop|restart
    * If bot crashes it'll be automatically restarted
    * It will also start after reboot

## Setting an admin

You have to set a variable `adminchatid` in `tokens.py` to be equal your chat_id or multiple chat_id (if more people will use your bot).
For example:

* `adminchatid = [443355]`
* `adminchatid = [443355, 55667788, 99884433]`

I will reimplement this differently later.
        
 
# PLEASE CONTRIBUTE :)
