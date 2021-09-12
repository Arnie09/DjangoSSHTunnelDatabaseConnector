import unittest
from datetime import datetime
import django
from freezegun import freeze_time

from DjangoSSHTunnelDatabaseConnector.Connector import form_insert_statement, form_delete_statement


class SimpleTest(unittest.TestCase):

    from django.conf import settings
    settings.configure(
        DATABASE_ENGINE='postgresql_psycopg2',
        DATABASE_NAME='db_name',
        DATABASE_USER='db_user',
        DATABASE_PASSWORD='db_pass',
        DATABASE_HOST='localhost',
        DATABASE_PORT='5432',
    )
    django.setup()

    @freeze_time("2012-01-14")
    def test_should_form_correct_insert_statement(self):
        from tests.mock_models import SampleModel

        data = {
            'sample_column': "some_value",
        }
        actual_insert_statement = form_insert_statement(SampleModel, data, ['id'])
        expected_insert_statement = 'INSERT INTO `sample_table` (`sample_column`,`date`,`null_column`,' + \
                                '`another_column`) VALUES ("some_value","' + str(datetime.now()) + '",' + \
                                'NULL,"sample");'

        self.assertEqual(actual_insert_statement, expected_insert_statement)

    def test_should_form_delete_statement_correctly(self):
        from tests.mock_models import SampleModel

        actual_delete_statement = form_delete_statement(SampleModel, 12)
        expected_delete_statement = "DELETE FROM `sample_table` WHERE (`id` = '12');"

        self.assertEqual(actual_delete_statement, expected_delete_statement)


if __name__ == '__main__':
    unittests.main()
