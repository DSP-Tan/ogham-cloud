# pydantic
pydantic is only ever telling you what should or shouldn't be in a given output or
input of the API.

It is how we tell fast api what the inputs to a given endooint will be. It's a way
of simply specifying the body/parameters of a given api call.

In models.py we have the actual object oriented representation of the table. We know
already we can insert just some columns, we know already how the id will be auto incremented
in the sql table.

Remember pydantic governs the inputs and outputs to the API. it will tell you what is returned after you do
a certain operation on it. It will tell you the form of the body, or the type of params that need to be
passed via curl or through a browser or through python requests package.

## Creating Schemas

To create the pydantic schemas you need to know how your endpoints will be operating.
Will there be path parameters in the query? If so these do not need to be a part of
the body.

How will the end point return information?

This needs to all be known before you design the schema.

# Alembic

Alembic is a way of ensuring that our database matches the model we have laid out
in models.py. This way we can document changes to the database structure as we
input them.

If changes are made on the database side, and were not registered in models.py,
running :
alembic revision --autogenerate -m "..."

Will produce python code which will restore the state of the database to who it is
laid out in models.py.

THis can be used to clean the database and keep it in a good state.

# SQL Alchemy

## Relationships in SQL alchemy



