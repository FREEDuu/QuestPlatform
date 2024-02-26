# Setup Fly.io

https://fly.io/docs/hands-on/install-flyctl/

https://fly.io/docs/django/getting-started/


## Django commands

| **Command** | **Purpose** |
|-------------|-------------|
| `python3 manage.py runserver` | Starts the development server. |
| `python3 manage.py makemigrations` | Creates new migrations based on the changes you have made to your models. |
| `python3 manage.py migrate` | Applies the changes made to your models to the database. |
| `python3 manage.py createsuperuser` | Creates a new superuser account. |
| `python3 manage.py startapp <app_name>` | Creates a new app within your Django project. |
| `python3 manage.py test <app_name>` | Runs tests for a specific app. |
| `python3 manage.py shell` | Opens the Python shell with the Django environment loaded. |
| `python3 manage.py collectstatic` | Collects all static files into a single directory. |
| `python3 manage.py sqlmigrate <app_name> <migration_file_name>` | Displays the SQL statements for a migration file. |


## Django Database api
https://docs.djangoproject.com/en/5.0/topics/db/queries/

| **Command** | **Purpose** |
|-------------|-------------|
| `Model.objects.all()` | Returns a QuerySet containing all objects in the database. |
| `Model.objects.create(**kwargs)` | Creates a new object with the specified keyword arguments and saves it to the database. |
| `Model.objects.filter(**kwargs)` | Returns a QuerySet containing objects that match the specified keyword arguments. |
| `Model.objects.get(**kwargs)` | Returns a single object that matches the specified keyword arguments. Raises a `DoesNotExist` exception if no match is found. |
| `Model.objects.exclude(**kwargs)` | Returns a QuerySet containing objects that do not match the specified keyword arguments. |
| `Model.objects.order_by(*fields)` | Returns a QuerySet containing objects sorted by the specified fields. |
| `Model.objects.values(*fields)` | Returns a QuerySet containing dictionaries of the specified fields for each object. |
| `Model.objects.annotate(*args, **kwargs)` | Returns a QuerySet containing annotated objects. |
| `Model.objects.aggregate(*args, **kwargs)` | Returns a dictionary containing the specified aggregations. |
| `Model.objects.count()` | Returns the number of objects in the database. |
| `Model.objects.first()` | Returns the first object in the database. |
| `Model.objects.last()` | Returns the last object in the database. |
| `Model.objects.none()` | Returns a QuerySet containing no objects. |

