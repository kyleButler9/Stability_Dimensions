import psycopg2
from panels.psql.config import config,StringTuple

TEST_COMMAND = ('SELECT \'connection to postgres established.\'',)
def batchExecuteSqlCommands(ini_section,SCHEMA=None,commands=TEST_COMMAND):
    # code from postgres python tutorial
    conn = None
    try:
        params = config(ini_section=ini_section)
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if SCHEMA:
            cur.execute(f"SET search_path='{SCHEMA}';")
        #  batch:
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

class DBAdmin:
    non_survey_columns=StringTuple(['time','notes','score','survey_id','customer_id'])
    createTableCommands = (
        """
        CREATE SCHEMA customers;
        """,
        """
        CREATE TABLE groups (
            group_id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            notes VARCHAR(255)
        );
        """,
        """
        CREATE TABLE customers(
            customer_id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            address VARCHAR(255),
            notes VARCHAR(255),
            group_id INTEGER NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups (group_id)
        );
        """,
        """
        CREATE TABLE survey(
            survey_id SERIAL PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            time timestamp,
            notes VARCHAR(255),
            score INTEGER,
            literacy INTEGER,
            income INTEGER,
            employability INTEGER,
            childcare INTEGER,
            english INTEGER,
            food INTEGER,
            skills INTEGER,
            education INTEGER,
            clothes INTEGER,
            housing INTEGER,
            safety INTEGER,
            health INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        );
        """,
        );
    initializeDatabaseCommands = (
        """
        INSERT INTO groups(name,notes)
        VALUES('None','Please select a group.'),('School',''),('Walk In','');
        """,
        """
        INSERT INTO customers(name,notes,group_id)
        VALUES('None','Please select a customer.',
                (SELECT group_id from groups where groups.name='None'));
        """,
    )
    dropTablesCommands = (
    """
    DROP TABLE if exists survey;
    """,
    """
    DROP TABLE IF EXISTS customers;
    """,
    """
    DROP TABLE IF EXISTS groups;
    """,
    """
    DROP SCHEMA IF EXISTS customers;
    """,
    )
if __name__ == '__main__':

    # This script instantiates a new PostgreSQL database.

    # In order to run, replace "local_launcher" below with the header of the .ini file
    # section.

    # For future development, consider compiling a CLI app that takes as input
    # a <example_path>.ini file path.

    #batchExecuteSqlCommands('local_stability',commands=DBAdmin.dropTablesCommands)
    #print('deleted beta schema.')
    batchExecuteSqlCommands('local_stability',SCHEMA='customer',commands=DBAdmin.createTableCommands)
    batchExecuteSqlCommands('local_stability',SCHEMA='customer',commands=DBAdmin.initializeDatabaseCommands)
