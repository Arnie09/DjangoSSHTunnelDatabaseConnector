import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder


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
        @param model: A standard Django model
        @param data: A dictionary with the keys as the fields of the Model and values containing the data that
                     is to be entered.
        @param fields_to_omit: A list of model fields that do not not need to be included in the insert statement.
                               Examples include primary keys.
        @return:
        """
        if self.connection is not None:
            cursor = self.connection.cursor()
            insert_statement = f"INSERT INTO `{model._meta.db_table}` ("
            VALUES = ' VALUES ('
            for field in model._meta.fields:
                field_name = field.name
                default_value = field.get_default()

                if field_name not in fields_to_omit:
                    insert_statement += f'`{field_name}`,'
                    if field_name not in data:
                        if default_value is None:
                            VALUES += f'NULL,'
                        else:
                            VALUES += f'"{default_value}",'
                    else:
                        VALUES += f'"{data[field_name]}",'
            insert_statement = insert_statement[:-1]
            VALUES = VALUES[:-1]
            insert_statement += ')'
            VALUES += ');'
            insert_statement += VALUES
            if self.verbose:
                print(insert_statement)
            cursor.execute(insert_statement)
            self.connection.commit()
            return cursor.lastrowid

    def delete(self, db_table, pk, pk_column='id'):

        if self.connection is not None:
            cursor = self.connection.cursor()
            delete_statement = f"DELETE FROM `{db_table}` WHERE (`{pk_column}` = '{pk}');"
            if self.verbose:
                print(delete_statement)
            got_deleted = cursor.execute(delete_statement)
            self.connection.commit()
            return got_deleted
