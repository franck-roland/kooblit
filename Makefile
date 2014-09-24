PROJECT_DIR = $(dir $(firstword $(MAKEFILE_LIST)))
PYTHONHOME ?= ${PROJECT_DIR}env/

PIP_VERSION = 1.5.6
PYTHON_VERSION = python2.7

CONFIG_TPL_FILE = ${PROJECT_DIR}config/config.tpl.yml
CONFIG_FILE = ${PROJECT_DIR}config/config.yml


##############
# Install    #
##############

install: setup_venv
	echo "Copying settings..."
	([ ! -f ${CONFIG_TPL_FILE} ] && echo "Project does not have a settings file.") || \
		([ -f ${CONFIG_FILE} ] && echo "Settings file already exists.") || \
			(cp -n ${CONFIG_TPL_FILE} ${CONFIG_FILE} && vi ${CONFIG_FILE})

##############
# Virtualenv #
##############


setup_venv: venv_init venv_deps

venv_init:
	(test -d ${PYTHONHOME} || virtualenv --python=${PYTHON_VERSION} --no-site-packages ${PYTHONHOME})
	${CFLAGS} ${PYTHONHOME}/bin/pip install --upgrade pip==${PIP_VERSION}

venv_deps:
	${CFLAGS} ${PYTHONHOME}/bin/pip install --upgrade -r $(PROJECT_DIR)requirements.txt


##############
# CleanUp    #
##############

clean:
	find . -path ./venv -prune -o -type f -name "*.pyc" -print0 -exec rm -f {} \;
	rm -r ${PYTHONHOME}