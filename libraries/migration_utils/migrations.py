from django.db import connections, DEFAULT_DB_ALIAS

from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader


def get(app_label, migration_name):
    """Returns migration object from app_label and migration name"""
    connection = connections[DEFAULT_DB_ALIAS]
    executor = MigrationExecutor(connection)
    return executor.loader.get_migration_by_prefix(app_label, migration_name)


def all():
    """Returns a dictionary of app names and their migrations"""
    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)
    graph = loader.graph

    app_labels = sorted(loader.migrated_apps)
    app_migrations = {}

    for app_label in app_labels:
        migrations = []
        for node in graph.leaf_nodes(app_label):
            for plan_node in graph.forwards_plan(node):
                if plan_node[0] == app_label:
                    # Give it a nice title if it's a squashed one
                    title = plan_node[1]
                    migrations.append(get(app_label, title))

        if migrations:
            app_migrations[app_label] = migrations

    return app_migrations


def applied():
    """Returns a dictionary of app names and applied migrations"""
    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)
    graph = loader.graph

    app_labels = sorted(loader.migrated_apps)
    app_migrations = {}

    for app_label in app_labels:
        migrations = []
        for node in graph.leaf_nodes(app_label):
            for plan_node in graph.forwards_plan(node):
                if plan_node[0] == app_label:
                    # Give it a nice title if it's a squashed one
                    title = plan_node[1]
                    if plan_node in loader.applied_migrations:
                        migrations.append(get(app_label, title))

        if migrations:
            app_migrations[app_label] = migrations

    return app_migrations


def unapplied():
    """ Returns a dictionary of app names and unapplied migrations"""
    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)
    graph = loader.graph

    app_labels = sorted(loader.migrated_apps)
    app_migrations = {}

    for app_label in app_labels:
        migrations = []
        for node in graph.leaf_nodes(app_label):
            for plan_node in graph.forwards_plan(node):
                if plan_node[0] == app_label:
                    # Give it a nice title if it's a squashed one
                    title = plan_node[1]
                    if not plan_node in loader.applied_migrations:
                        migrations.append(get(app_label, title))

        if migrations:
            app_migrations[app_label] = migrations

    return app_migrations
