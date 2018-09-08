# REST key-val

A key value storing API.

## Installation

### Requirements
* Redis
* Python 3.3 and up

  `$ pip install -r requirements.txt`

### Redis configuration (for persistant storage)

* Start Redis server locally in port 6379
* Update redis conf file, insert the following lines -

  `appendonly yes`

  `appendfsync everysec`

### Start Flask server

* Start Flask server by running this command -

  `$ python app.py`
