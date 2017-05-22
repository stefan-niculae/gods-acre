# Generation

## Admin
 - create admin: `./manage.py createsuperuser`
 - dump fixtures: `./manage.py dumpdata --format=yaml auth.user > cemetery/fixtures/admin.yaml`

## Cemetery
 - add models in django-admin
 - dump fixtures: `./manage.py dumpdata --format=yaml cemetery > cemetery/fixtures/cemetery.yaml`

# TODO
 - implement `get_by_natural_key` and `natural_key` for each model to be serialized https://docs.djangoproject.com/en/1.11/topics/serialization/#serialization-formats