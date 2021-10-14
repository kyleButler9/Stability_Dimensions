import psycopg2
try:
    from panels.psql.config import read_config_file,ptuple
except:
    from config import read_config_file,ptuple


TEST_COMMAND = ('SELECT \'connection to postgres established.\'',)
def batchExecuteSqlCommands(ini_section,SCHEMA=None,commands=TEST_COMMAND):
    # code from postgres python tutorial
    conn = None
    try:
        params = read_config_file(ini_section=ini_section)
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
def create_schema(ini_section,SCHEMA):
    conn = None
    try:
        params = read_config_file(ini_section=ini_section)
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(f"CREATE SCHEMA {SCHEMA};")
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
class DBAdmin:
    non_survey_columns=ptuple(['time','notes','score','survey_id','customer_id'])
    createTableCommands = (
        """
        CREATE TABLE categories (
            category SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            notes VARCHAR(255)
        );
        """,
        """
        CREATE TABLE classes (
            class SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            notes VARCHAR(255),
            category INTEGER NOT NULL,
            FOREIGN KEY (category) REFERENCES categories (category)
        );
        """,
        """
        CREATE TABLE customers(
            customer SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            address VARCHAR(255),
            notes VARCHAR(255),
            referral VARCHAR(255),
            class INTEGER NOT NULL,
            FOREIGN KEY (class) REFERENCES classes (class)
        );
        """,
        """
        CREATE TABLE survey(
            survey_id SERIAL PRIMARY KEY,
            customer INTEGER NOT NULL,
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
            FOREIGN KEY (customer) REFERENCES customers (customer)
        );
        """,
        )
    initializeDatabaseCommands = (
        """
        CREATE FUNCTION on_new_cat()
        RETURNS TRIGGER
        language plpgsql
        as
        $$
        begin
        INSERT INTO classes(name,category,notes) 
        VALUES(
            CONCAT(NEW.name,'_general'),
            (
            SELECT category
            FROM categories
            WHERE name = NEW.name
            ),
            CONCAT('umbrella class for category ',NEW.name)
        );
        RETURN NEW;
        END;
        $$;

        CREATE TRIGGER new_cat_inserted
        AFTER INSERT
        ON Categories
        FOR EACH ROW
        EXECUTE PROCEDURE on_new_cat();
        """,
        """
        INSERT INTO categories(name)
        VALUES('None'),('School'),('Walk In');
        """,
        """
        INSERT INTO customers(name,notes,class)
        VALUES('None','Please select a customer.',
                (SELECT class from classes where classes.name='None_general'));
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
    DROP TABLE IF EXISTS classes;
    """,
    """
    DROP TABLE IF EXISTS categories;
    """,
    """
    DROP FUNCTION on_new_cat
    """,
    """
    DROP SCHEMA IF EXISTS customers;
    """,
    )
if __name__ == '__main__':

    # This script instantiates a new PostgreSQL database.

    # In order to run, replace "demo" below with the header of the .ini file
    # section.

    # For future development, consider compiling a CLI app that takes as input
    # a <example_path>.ini file path.

    batchExecuteSqlCommands('local_stability',SCHEMA='customers',commands=DBAdmin.dropTablesCommands)
    #print('deleted beta schema.')
    create_schema('local_stability','customers')
    batchExecuteSqlCommands('local_stability',SCHEMA='customers',commands=DBAdmin.createTableCommands)
    batchExecuteSqlCommands('local_stability',SCHEMA='customers',commands=DBAdmin.initializeDatabaseCommands)
