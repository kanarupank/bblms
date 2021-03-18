# Python version used 3.9.2

python -V

# pip version used 21.0.1

pip -V

# install virtualenv tool and create environment

pip install virtualenv

virtualenv -p python env

# activate the source

source evn/bin/activate (in Mac/Linux)
\env\Scripts\activate.bat (Windows)

# install requirements, check other versions in the requirements.txt

pip install -r requirements.txt

# create DB (writes to the db.sqlite3 file)

python manage.py migrate

# populate DB with fake data

python manage.py seeder --mode=refresh

# start server and check http://127.0.0.1:8000/

python manage.py runserver

# view swagger documentation with http://127.0.0.1:8000/swagger

# check artifacts directory to find class, entity diagrams

#Assumptions
Team and squad not differentiated as unlimited substitutions are allowed in basketball - no rosters
This is for a particular tournament
Coach could view only his/her team details
No realistic date values expected (random dates per games)
The requirement of games view where it ‘will reflect how the competition progressed and who won. ‘ - the round information will reflect that
The coach’s requirement is to get hte 90th percentile top players within their own team
Coach cannot create team
Only admin does and that too only for 16 teams
