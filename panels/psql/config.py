from configparser import ConfigParser
import psycopg2
from os.path import join,dirname
#   config returns a dictionary
def config(ini_file='database.ini', ini_section='local_stability'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(join(dirname(__file__),ini_file))
    # get section, default to postgresql
    db = {}
    if parser.has_section(ini_section):
        params = parser.items(ini_section)
        for param in params:
            db[param[0]] = param[1]
    elif len(parser.read(ini_file)) == 0:
        raise Exception("No {0} in same directory as {1}".format(ini_file,__file__))

    else:
        raise Exception('Section {0} not found in the {1} file'.format(ini_section, ini_file))
    return db

RETRY_CONNECTION_MAX_COUNT = 5

class tuple(tuple):
    # a method that allows smoother transition
    # between python and postgre tuples
    def string_repr(self):
        s=["("]
        for i in self:
            s.append("'"+str(i)+"',")
        s[-1]=s[-1][:-1]+")"
        return ''.join(s)

class DBI:
    def __init__(self,SCHEMA='customers',**kwargs):
        # at the start of every scession need to run "set search_path = beta;"
        # then you can drop beta. everywhere
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
        self.schema=SCHEMA
        self.connectToDB()

    def connectToDB(self,**kwargs):
        try:
            # read database configuration
            # if self.conn: #is not None
            #     self.conn.close()
            if 'try_count' in kwargs:
                try_count = kwargs['try_count']
            else:
                try_count=0
            if "ini_section" in kwargs:
                self.ini_section=kwargs['ini_section']

            params = config(ini_section=self.ini_section)
            self.conn=None
            self.conn = psycopg2.connect(**params)
            self.cur = self.conn.cursor()
            if 'schema' in kwargs:
                self.schema=kwargs['schema']
            else:
                self.schema='customers'
            self.cur.execute(f"SET search_path='{self.schema}';")
            self.conn.commit()
            self.cur.execute('show search_path;')
            if self.cur.fetchone()[0] != self.schema:
                if try_count < RETRY_CONNECTION_MAX_COUNT:
                    print('failed conn or search_path setting to ',self.schema,try_count,'times.')
                    try_count+=1
                    # this function recursively calls itself here to reattempt the connection
                    self.connectToDB(ini_section=self.ini_section,try_count=try_count,schema=self.schema)
                else:
                    print('failed conn or search_path setting to ',self.schema,try_count,'times.')
                    print('No more attempts... check cable.')
            else:
                print('Connected. active schema: ',self.schema)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.conn = None
        finally:
            return self
    def restartConnection(self,**kwargs):
        # recursively try to restart the connection to database.
        attempt=kwargs['attempt']
        if 'attlim' in kwargs:
            attlim =kwargs['attlim']
        else:
            attlim=5
        if 'connKwargs' in kwargs:
            connKwargs=kwargs['connKwargs']
        else:
            connKwargs=dict()
        if attempt < attlim:
            print('retrying connection...attempt #',attempt)
            self.connectToDB(**connKwargs)
            if self.testConnection()==True:
               return 'Connection re-established.'
            else:
                attempt+=1
                self.restartConnection(attempt=attempt,attlim=attlim,connKwargs=connKwargs)
        else:
            return 'Connection unable to be re-established.'
    def execute_and_commit(self,sql,*args):
        try:
            cur = self.conn.cursor()
            cur.execute(sql,(*args,))
            try:
                ret=cur.fetchone()
            except:
                ret='operation successful.\nNo return requested.'
            finally:
                cur.close()
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            if self.testConnection()==True:
                print(error)
                ret = error
            else:
                ret='connection dropped.'
        finally:
            return ret

    def insertToDB(self,sql,*args):        
        return self.execute_and_commit(self,sql,*args)

    def fetchone(self,sql,*args):
        #returns one tuple
        # does not commit
        try:
            if self.testConnection() == False:
                self.restartConnection()
            self.cur = self.conn.cursor()
            if len(args) != 0:
                self.cur.execute(sql,(*args,))
            else:
                self.cur.execute(sql)
            return self.cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def fetchall(self,sql,*args):
        #returns a list of tuples
        # does not commit
        if self.testConnection() == False:
            self.restartConnection()
        if len(args) != 0:
            self.cur.execute(sql,(*args,))
        else:
            self.cur.execute(sql)
        return self.cur.fetchall()
    def testConnection(self):
        try:
            self.cur.execute("SELECT 1")
            back = self.cur.fetchone()[0]
        except:
            back = 0
        finally:
            return back
if __name__ == "__main__":
    db = DBI(ini_section='local_launcher')
    print('is connected: ',db.testConnection()==True)