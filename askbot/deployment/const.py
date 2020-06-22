DEFAULT_PROJECT_NAME = 'askbot_site'

SQLITE = 2
DB_ENGINE_CHOICES = (
    (1, 'PostgreSQL'),
    (SQLITE, 'SQLite'),
    (3, 'MySQL'),
    (4, 'Oracle')
)
ROOT_DIR_HELP = 'Root directory (relative or absolute) for the Django project (for the manage.py file)'
PROJ_NAME_HELP = 'Project directory name (subdirectory for the settings.py, urls.py files)'
