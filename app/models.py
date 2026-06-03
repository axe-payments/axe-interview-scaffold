"""Your database models go here.

Tortoise ORM is already connected to Postgres, and `generate_schemas=True` in
app/main.py auto-creates a table for every model you define here when the app starts.
So: add a model, restart the app (it hot-reloads), and the table exists. No migrations.

You do not have to use the database at all — you can keep workflow definitions in code
or a config file if you prefer. It's here if you want to persist workflows, executions,
step logs, etc.

Example (delete or replace):

    from tortoise import fields
    from tortoise.models import Model

    class ExampleModel(Model):
        id = fields.UUIDField(pk=True)
"""
