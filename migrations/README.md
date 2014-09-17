Beats Database Migration
========================

Using Alembic with a generic single-database configuration

Creating a Migration Script
---------------------------

`$ alembic revision -m "script_description"`

This generates a new file in /migrations/versions

Edit the `upgrade()` and `downgrade()` functions 
in the file to do what you want

Running a Migration
-------------------

`$ alembic upgrade head`

Upgrades to most recent revision

You can also do relative upgrades and downgrades with 
`$ alembic upgrade +1` and `$ alembic downgrade -1` by 
specifying how many versions to moves from the current one.