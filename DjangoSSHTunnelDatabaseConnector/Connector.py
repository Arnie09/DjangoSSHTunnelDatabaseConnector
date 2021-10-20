import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

NON_CHARACTER_DTYPES = ['BooleanField', 'IntegerField', 'BigIntegerField']


def ifNoneReturnNull(data, use_quotes):
    if data is None:
        return f"NULL, "
    if use_quotes:
        return f"'{data}', "
    else:
        return f"{data}, "


def form_insert_statement(model, data, fields_to_omit):
    insert_statement = f"INSERT INTO `{model._meta.db_table}` ("
    VALUES = ' VALUES ('
    for field in model._meta.fields:
        field_name = field.name
        data_type = field.get_internal_type()
        default_value = field.get_default()

        if field_name not in fields_to_omit:
            insert_statement += f'`{field_name}`,'
            if field_name not in data:
                if default_value is None:
                    VALUES += f"NULL, "
                else:
                    VALUES += f"'{default_value}', "
            else:
                if data_type in NON_CHARACTER_DTYPES:
                    VALUES += ifNoneReturnNull(data[field_name], False)
                else:
                    VALUES += ifNoneReturnNull(data[field_name], True)
    insert_statement = insert_statement[:-1]
    VALUES = VALUES[:-2]
    insert_statement += ')'
    VALUES += ');'
    insert_statement += VALUES
    return insert_statement


def form_delete_statement(model, pk, pk_column='id'):
    return f"DELETE FROM `{model._meta.db_table}` WHERE (`{pk_column}` = '{pk}');"


def form_update_statement(model, data, pk, pk_column='id'):
    UPDATE_STATEMENT = f"UPDATE `{model._meta.db_table}` SET "
    for field in model._meta.fields:
        field_name = field.name
        data_type = field.get_internal_type()
        if field_name in data:
            if data_type in NON_CHARACTER_DTYPES:
                UPDATE_STATEMENT += f"`{field_name}` = {ifNoneReturnNull(data[field_name], False)}"
            else:
                UPDATE_STATEMENT += f"`{field_name}` = {ifNoneReturnNull(data[field_name], True)}"

    UPDATE_STATEMENT = UPDATE_STATEMENT[:-2]  # removing the extra , and ' ' at the end of the column
    UPDATE_STATEMENT += f" WHERE (`{pk_column}` = '{pk}');"
    return UPDATE_STATEMENT


class Connector:

    def __init__(self, ssh_host, ssh_port, ssh_username, ssh_password, database_username, database_password,
                 database_name, localhost, verbose=True):
        self.connection = None
        self.tunnel = None
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.database_username = database_username
        self.database_password = database_password
        self.database_name = database_name
        self.localhost = localhost
        self.verbose = verbose

        self.open_ssh_tunnel()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mysql_disconnect()
        self.close_ssh_tunnel()

    # Disconnectors
    def mysql_disconnect(self):
        """Closes the MySQL database connection.
        """
        if self.connection is not None:
            self.connection.close()

    def close_ssh_tunnel(self):
        """Closes the SSH tunnel connection.
        """
        self.tunnel.close()

    # Connectors
    def open_ssh_tunnel(self):

        if self.verbose:
            sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG

        self.tunnel = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_username,
            ssh_password=self.ssh_password,
            remote_bind_address=(self.localhost, 3306)
        )
        self.tunnel.start()

        self.mysql_connect()

    def mysql_connect(self):

        self.connection = pymysql.connect(
            host=self.localhost,
            user=self.database_username,
            passwd=self.database_password,
            database=self.database_name,
            port=self.tunnel.local_bind_port
        )

    # utilities CRUD operations need to be written here

    def create(self, model, data, fields_to_omit):
        """
        This is the function that is used to insert items in to the remote database
        :param model: A standard Django model
        :param data: A dictionary with the keys as the fields of the Model and values containing the data that
                     is to be entered.
        :param fields_to_omit: A list of model fields that do not not need to be included in the insert statement.
                               Examples include primary keys.
        :return int: the id of the last record inserted.
        """
        if self.connection is not None:
            cursor = self.connection.cursor()
            insert_statement = form_insert_statement(model, data, fields_to_omit)
            if self.verbose:
                print(insert_statement)
            cursor.execute(insert_statement)
            self.connection.commit()
            return cursor.lastrowid

    def delete(self, model, pk, pk_column='id'):
        """
        This function is used to delete a single record of a model
        :param model: The name of the Model whose record you want to delete.
        :param pk: The pk of the record you want to delete.
        :param pk_column: The name of the pk field.
        :return int: 1 for successful deletion and 0 for failure.
        """
        if self.connection is not None:
            cursor = self.connection.cursor()
            delete_statement = form_delete_statement(model, pk, pk_column)
            if self.verbose:
                print(delete_statement)
            got_deleted = cursor.execute(delete_statement)
            self.connection.commit()
            return got_deleted

    def batch_delete(self, model, list_of_pk, pk_column='id'):
        """
        This method is used to batch deletion of records
        :param model: The name of the model whose object you want to delete
        :param list_of_pk: list of pk you want to delete
        :param pk_column: name of the pk column
        :return list[int]: list of responses for all the pks received.
        """
        response = []
        for pk in list_of_pk:
            response.append(self.delete(model, pk, pk_column))
        return response

    def read(self, model, query):
        """
        This method is used to read query sets of data and parse those results as Django objects
        :param model: Model whose data you want to parse
        :param query: actual filter query in ORM.query
        :return: list[Model]: list of model objects returned as a result
        """
        if self.connection is not None:
            cursor = self.connection.cursor()
            query_str = str(query)
            if self.verbose:
                print(query_str)

            # execution of the actual query
            cursor.execute(query_str)

            # reading the column names from the query
            desc = cursor.description
            column_names = [col[0] for col in desc]

            data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            django_col_sql_map = {}

            # creating a map of django column names and mysql table column names because sometimes they are different
            for field in model._meta.fields:
                field_name_tuple = field.get_attname_column()
                django_col_sql_map[field_name_tuple[1]] = field_name_tuple[0]

            result_set = []
            for results in data:
                model_object = model()
                for key in results:
                    setattr(model_object, django_col_sql_map[key], results[key])
                result_set.append(model_object)

            return result_set
        else:
            raise Exception('Connection error!')

    def update(self, model, data, pk, pk_column='id'):
        """
        This method can be used to update the fields of a model with specific primary key
        :param model: Model whose data you want to update
        :param data: Updated values of columns you want to update in a dictionary k-v format
        :param pk: pk of the row whose data you want to update
        :param pk_column: name of the column of pk, default is 'id'
        :return: int - 1 for updated, 0 for no update
        """
        if self.connection is not None:
            cursor = self.connection.cursor()
            update_statement = form_update_statement(model, data, pk, pk_column)
            if self.verbose:
                print(update_statement)
            got_updated = cursor.execute(update_statement)
            self.connection.commit()
            return got_updated

    def batch_update(self, model, data, pk, pk_column='id'):
        """
        This method is used to perform batch update operation on a number of db records.
        :param model: Model whose data you want to update.
        :param data: List[Dictionary] Updated values of the rows
        :param pk: List[int] pks of records you want to update
        :param pk_column: name of the column of pk, default is 'id'
        :return: list[int] - 1 for for updated, 0 for no update.
        """

        if self.connection is not None:
            updated = []
            for record, primary_key in zip(data, pk):
                updated.append(self.update(model, record, primary_key, pk_column))
            return updated

    def execute_raw_query(self, query):
        """
        This method is used to execute raw sql query and return response. This is ideal for update, delete and add
        operations
        :param query: Raw sql query to be applied
        :return: return response
        """

        if self.connection is not None:
            cursor = self.connection.cursor()
            response = cursor.execute(query)
            self.connection.commit()
            return response
