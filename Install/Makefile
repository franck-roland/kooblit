

all: update apache pip virtualenv git lxml mongo libffi

apache:
	sudo apt-get install apache2

update:
	sudo apt-get update

pip:
	sudo apt-get install python-pip

virtualenv:
	sudo pip install virtualenv 
	sudo pip install virtualenvwrapper

postgresql:
	sudo apt-get install libpq-dev python-dev
	sudo apt-get install postgresql postgresql-contrib
	export PATH=${PATH}:/usr/lib/postgresql/9.1/bin

git:
	sudo apt-get install git

lxml:
	sudo apt-get install libxml2-dev libxslt-dev

libffi:
	sudo apt-get install libffi-dev

mongo:
	sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
	echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
	sudo apt-get update
	sudo apt-get install mongodb-org
	sudo service mongod start
