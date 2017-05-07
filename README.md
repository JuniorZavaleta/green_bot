# Green Bot

Recommend use Linux

### Install MySql

https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04

### Install drivers for mysql and python and pip

```
sudo apt-get install python-pip python-dev libmysqlclient-dev
```

### Installation

Clone the project

```
git clone https://github.com/JuniorZavaleta/green_bot
```

Go to the directory

```
cd green_bot
```

Create a virtual env
```
virtualenv venv --distribute
```

Activate the virtual env
```
source venv/bin/activate
```

Install the dependencies
```
pip install -r requirements.txt
```

### Deployment
Use ngrok and configure your webhook

Download ngrok

https://ngrok.com/download

Execute ngrok

./path/to/ngrok http 5000

Flask use port 5000 by default

Copy the https url (i.e. https://abc123.ngrok.io)

On bot.py
Set your telegram token on TELEGRAM_TOKEN
And your https url of ngrok on SITE_URL

Enter to "https://your_site_url/set" for set the telegram webhook

Use the bot.
