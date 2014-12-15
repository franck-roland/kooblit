kooblit
=======


Requirements
------------

- Python 2.7.x + virtualenv + pip
- Postgresql (install with brew on MacOSX or apt-get on linux)
- Mongo (install with brew on MacOSX or apt-get on linux)
- Apache server

# Installation #
---

In Install directory: `make`

## Installation of the databases systems ##

### Mongo Installation ###
Use mongod and the script given in *installation_mongo* to create the document and the user

### Postgresql Installation ###
Use the instructions sequences described in *installation_postgres*

## Right for static directories used in local ##
Use the script *installation_droits_serveur*

## Virtualenv setting ##
1.  In you file .bashrc (In your home directory), add the lines written in the file *set_bashrc*.
2.  Use the script *set_virtualenv.sh* to set your env for the first time

