import os
import traceback

import django
from django.apps import apps
from django.db import connection
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fpl.settings')
django.setup()

def reset_migrations_and_drop_tables():
    # Get all the apps in the project
    all_apps = [app for app in apps.get_app_configs() if app.name not in [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_extensions',
        'django_filters',
        'widget_tweaks',
        'bootstrap_modal_forms',
        'fpl',
    ]]

    with connection.cursor() as cursor:
        # Iterate over each app
        for app in all_apps:
            print(f"Resetting migrations and dropping tables for app: {app.label}")

            # Drop constraints associated with the app's models
            for model in app.get_models():
                drop_many_to_many_tables(model)
                table_name = model._meta.db_table
                try:
                    for constraint in model._meta.constraints:
                        if constraint.name != 'pk_' + table_name:  # Skip primary key constraint
                            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint.name};")
                            print(f"Dropped constraint: {constraint.name} on {table_name}")
                except Exception as e:
                    print(f"Error dropping constraint on {table_name}: {e}")

            # Drop each table associated with the app
            for model in app.get_models():
                table_name = model._meta.db_table
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                    print(f"Dropped table: {table_name}")
                except Exception as e:
                    print(f"Error dropping table {table_name}: {e}")

            # Reset migrations for the app
            app_migrations_path = os.path.join(app.path, 'migrations')
            if os.path.exists(app_migrations_path):
                for migration_file in os.listdir(app_migrations_path):
                    migration_file_path = os.path.join(app_migrations_path, migration_file)
                    if migration_file != '__init__.py' and os.path.isfile(migration_file_path):
                        try:
                            os.remove(migration_file_path)
                            print(f"Deleted migration file: {migration_file}")
                        except Exception as e:
                            print(f"Error deleting file {migration_file}: {e}")

                # Delete migration records for the app from the django_migrations table
            try:
                cursor.execute("DELETE FROM django_migrations WHERE app = %s;", [app.label])
                print(f"Deleted migration records for app: {app.label}")
            except Exception as e:
                print(f"Error deleting migration records for app {app.label}: {e}")

    # Make migrations and migrate for all apps
    apps.clear_cache()
    connection.close()
    try:
        call_command('makemigrations')
        call_command('migrate')
    except Exception as e:
        print(f"Error during migrations")
        traceback.print_exc()

def drop_many_to_many_tables(model):
    """Drop all ManyToManyField tables for a given model."""
    with connection.cursor() as cursor:
        for field in model._meta.get_fields():
            if field.many_to_many and not field.auto_created:  # Check for ManyToMany fields
                table_name = field.remote_field.through._meta.db_table
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                    print(f"Dropped ManyToMany table: {table_name}")
                except Exception as e:
                    print(f"Error dropping ManyToMany table {table_name}: {e}")

if __name__ == '__main__':
    reset_migrations_and_drop_tables()