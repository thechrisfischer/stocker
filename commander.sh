#!/bin/bash

# SQLite database - no external database server needed
export DATABASE_URL="sqlite:///stocker.db"

function db_setup() {
    source venv/bin/activate
    flask create-db
}

function db_backup() {
    if [ -f "stocker.db" ]; then
        sqlite3 stocker.db ".backup backups/stocker-$(date +%Y%m%d-%H%M%S).db"
        echo "Backup created in backups/"
    else
        echo "No database file found"
    fi
}

# check if a venv exists, if not create and activate it
function create_virtualenv() {
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
}

# install python dependencies
function python_setup() {
    source venv/bin/activate
    pip install -r requirements.txt
}

# go into the static node directory and install npm packages
function npm_setup() {
    cd static || exit
    npm install
    npm run build
    cd ..
}

function start() {
    source venv/bin/activate
    flask run --port 5000 &
    cd static || exit
    npm start &
    cd ..
}

function stop() {
    lsof -n -i:3000 | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null
    lsof -n -i:5000 | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null
}

case "$1" in
    setup)
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
    backup)
        db_backup
        ;;
    refresh_db)
        rm -f stocker.db
        db_setup
        ;;
    *)
        echo $"Usage: $0 {setup | startapp | stopapp | backup | refresh_db}"
esac
