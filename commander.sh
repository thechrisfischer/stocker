#!/bin/bash

# setup global application config here
export DATABASE_URL="postgresql://stocker:stocker@localhost/assets"

# setup a database if it hasn't been done so
function db_init() {
    psql -c "create database stocker;"
    psql -c "create user stocker with password 'stocker' CREATEDB;"
}

function db_drop() {
    psql -c "drop database stocker;"
}

function db_setup() {
    export DATABASE_URL="postgresql://stocker:stocker@localhost/stocker"
    python3 manage.py create_db
}

# check if a venv exists, if not create activate it
function create_virtualenv() {
    if [ ! -d "venv" ]; then
        virtualenv -p python3 venv
    fi
}

# install python dependencies (python3)
function python_setup() {
    source venv/bin/activate
    which python
    pip3 install -r requirements.txt
}

# go into the static node directory and install npm packages
function npm_setup() {
    cd static || exit
    npm run build
    npm install
    cd ..
}

function start() {
    source venv/bin/activate
    python3 manage.py runserver &
    cd static || exit
    npm start &
    cd ..
}

function stop() {
    lsof -n -i:3000 | grep LISTEN | awk '{print $2}' | xargs kill
    lsof -n -i:5000 | grep LISTEN | awk '{print $2}' | xargs kill

}

case "$1" in
    setup)
        db_init
        create_virtualenv
        python_setup
        npm_setup
        db_setup
        ;;
    startapp)
        start
        ;;
    stopapp)
        stop
        ;;
    refresh_db)
        db_drop
        db_init
        ;;
    *)
        echo $"Usage: $0 {setup | startapp | stopapp | refresh_db}"
esac
