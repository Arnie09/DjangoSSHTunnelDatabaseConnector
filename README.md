# Django-SSHTunnel-Database-Connector
## _The way to talk to databases via ssh in the django way_

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

This library helps to connect to remotely hosted databases and helps to do CRUD operations using Django models in a way that is familiar to using Django ORMs.

### Installation:

To install the latest version of this library, write this in your terminal.
```
    pip install django-ssh-tunnel-database-connector
```


### Usage: 

#### CREATE:

Let's say you have a Django model in a remote database like this: 
    
```
class RemoteModel(models.Model):
    
    class Meta:
        db_table = 'remote_model'
       
    example_field_one = models.CharField(default="default_value")
    example_field_two = models.CharField(default="another_default_value")
```

For this kind of Model, if we want to insert data into the table, we write the following code:

```
from DjangoSSHTunnelDatabaseConnector import Connector

with Connector(ssh_host, ssh_port, ssh_username, ssh_assword,
               database_username, database_password, database_name, 
               localhost, verbose=False) as sshTunnelDatabaseConnector:

    # the dictionary of all the fields and data that you want to enter
    # if your model has columns that has default values that you donot
    # want to change, you need not have them here.
    data = {"example_field_one": data_you_want_to_insert}
    
    model_id = sshTunnelDatabaseConnector.create(Model, data, ["id"])
```

Thus, _create()_ requires the following arguments:
* Model = Name of the model whose record you want to insert.
* data = the data to be inserted in the form of k-v pair in a dictionary
* columns_to_omit = name of the columns in the db whose value you dont want 
  to include in the INSERT statment. 

Notice the fact that we did not mention what would be the value of the second
field of the model. In case it is not mentioned, it's going to take the default
value specified in the model. 

#### DELETE:

In order to delete a record in the remote db, you would need to know the id of the
record you want to delete. Usage of delete: 

```
from DjangoSSHTunnelDatabaseConnector import Connector

with Connector(ssh_host, ssh_port, ssh_username, ssh_assword,
               database_username, database_password, database_name, 
               localhost, verbose=False) as sshTunnelDatabaseConnector:

    # The response object is 1 if the data was deleted, 0 if it failed. 
    response = sshTunnelDatabaseConnector.delete(Model, pk, pk_column)
```

Thus, _delete()_ requires the following arguments: 
* Model = Name of the model whose record you want to delete.
* pk = value of the primary key
* pk_column = name of the pk column. If nothing is mentioned, the default name 'id'
  is used. 

#### READ:

In order to read you need only two things: model and the django ORM query in sql form.
The way to form Django ORM query in SQL is to just write a filter query and add `.query` at the end

```
from DjangoSSHTunnelDatabaseConnector import Connector

with Connector(ssh_host, ssh_port, ssh_username, ssh_assword,
               database_username, database_password, database_name, 
               localhost, verbose=False) as sshTunnelDatabaseConnector:
               
    # The response of the object is an array of model objects that are read from the database
    query = Model.objects.filter(some_column="filter_word")
    model_objects = sshTunnelDatabaseConnector.read(Model, query) 
```

This _read()_ requires the following arguments:

* Model = Name of the model whose record you want to read.
* query = Django orm sql query.

#### UPDATE:

In order to update, you need the following three things: model, data, pk and pk column name is optional

```
from DjangoSSHTunnelDatabaseConnector import Connector
with Connector(ssh_host, ssh_port, ssh_username, ssh_assword,
               database_username, database_password, database_name, 
               localhost, verbose=False) as sshTunnelDatabaseConnector:
               
    # The response of the object is an array of model objects that are read from the database
    data = {"example_field_one": data_you_want_to_insert}
    model_objects = sshTunnelDatabaseConnector.update(Model, data, 69) 
```

This _update()_ function takes the following arguments:

* Model = Name of the model whose record you want to update
* data = Dictionary of column and updated records as K-V 
* pk = primary key of the record you want to update.
  
### Other Utility Functions: 

There are some other utility functions to make the life simpler. Those are: 
 * _batch_delete()_ - This can be used to delete a list of records in a single function call. 
 * _batch_update()_ - This can be used to update a bunch of records together in a single call. 