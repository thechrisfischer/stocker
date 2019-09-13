# Skeleton Application Flask / React / sqlalchemy

* Python 3.x
* Pytest
* Heroku
* Flask
* React
* Redux
* React-Router 2.0
* React-Router-Redux
* Babel 6
* SCSS processing
* Webpack


### Scripted setup
Setup a database (only should have do this once)
```
psql
create database stocker;
create user assets with password 'stocker' CREATEDB;
```

This will setup the application using commander
```
source commander.sh setup
```

Start the application
```
./commander startapp
```

Stop the application
```
./commander stopapp
```

### Manual install
If pip is not installed, you can follow this simple article to [get both homebrew and python](https://howchoo.com/g/mze4ntbknjk/install-pip-on-mac-os-x)

After you install python, you can optionally also install python 3

```
$ brew install python3
```

You should use virtual environments when running this project
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Create DB
```sh
$ export DATABASE_URL="postgresql://username:password@localhost/mydatabase"

or

$ export DATABASE_URL="mysql+mysqlconnector://username:password@localhost/mydatabase"

or

$ export DATABASE_URL="sqlite:///your.db"

More about connection strings in this [flask config guide](http://flask-sqlalchemy.pocoo.org/2.1/config/)

$ python manage.py create_db
```

To update database after creating new migrations, use:

```sh
$ python manage.py db upgrade
```

### Install Front-End Requirements
```sh
$ cd static
$ npm install
```

### Run Back-End

```sh
$ python manage.py runserver
```

### Test Back-End

```sh
$ python test.py --cov-report=term --cov-report=html --cov=application/ tests/
```

### Run Front-End

```sh
$ cd static
$ npm start
```

### Build Front-End

```sh
$ npm run build:production
```


Now, you can decide on which database you wish to use.


Note: you do not need to run "python manage.py db upgrade" or "python manage.py db migrate" if its your first go at it

4. Run Back-End

```
$ python manage.py runserver
```

If all goes well, you should see ```* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)``` followed by a few more lines in the terminal.

5. open a new tab to the same directory and run the front end

```
$ cd static
$ npm install
$ npm start
```

6. open your browser to http://localhost:3000/register and setup your first account
7. enjoy! By this point, you should be able to create an account and login without errors.

###postgres tips###
hit the elephant at the top and open up assets, it will pull up termianl on the UI

OR

psql

\c   ----> connect
\d ----> view schema
\d asset ---> view headers in table

##How to update the schema in postgres##

Step 1: source venv/bin/activate  (this activates virtual environment)
Step 2: export DATABASE_URL="INSERT THE URL"
to get URL, type

git grep DATABASE_URL and this will find it

Step 3: python3 manage.py db (this is a script, nto a command)
Step 4: python3 manage.py db migrate (preparation)
Step 3: python3 manage.py db upgrade (execution - adds any additional headers for example)

Option: python3 manage.py db downgrade (ROLLBACK)
