# Build
- (optional) create virtualenv: ```mkvirtualenv --python=`which python3` gods-acre```
- download dependencies: `pip install requirements.txt`

# Setup DB
- (optional) delete old db: `rm db.sqlite3`
- create models: `./manage.py migrate --run-syncdb`
- load fixtures: `./manage.py loaddata cemetery/fixtures/*.yaml`

# Run
`./manage.py runserver`

# Dev
Enter virtualenv: `workon gods-acre`

## shell
- `./manage.py shell`
- `from cemetery.models import *`
- create: `Spot(parcel='A', row=2, column=5).save()`
- read: `Spot.objects.all()` or `Spot.objects.get(id=1)` or `Spot.objects.filter(parcel__contains='a')`
- update: `Spot.objects.first().parcel = 'b'`
- delete
- changes aren't saved to db until commit: `spot.save()`

## translation
- pull out all strings marked for translation: `./manage.py makemessages -l ro` (it will not overwrite existing translations)
  - install os dependencies before `brew install gettext` / `sudo apt-get install gettext`
- open `locale/<your language code>/LC_MESSAGES/django.po` and provide a `msgstr` for each `msgid`
- compile into `.mo` with `./manage.py compilemessages`

