from configparser import ConfigParser
import psycopg2
from os.path import join,dirname
#   config returns a dictionary
def read_config_file(ini_file='database.ini', ini_section='local_stability'):
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

class ptuple(tuple):
    # a method that allows smoother transition
    # between python and postgre tuples
    def string_repr(self):
        s=["("]
        for i in self:
            s.append("'"+str(i)+"',")
        s[-1]=s[-1][:-1]+")"
        return ''.join(s)

class DBI:
    conn=None
    MAX_CONNECTION_ATTEMPTS=5
    def __init__(self,SCHEMA='customers',**kwargs):
        # at the start of every scession need to run "set search_path = beta;"
        # then you can drop beta. everywhere
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
        self.schema=SCHEMA
        self.connectToDB()

    def connectToDB(self,**kwargs):
        try:
            if "ini_section" in kwargs:
                self.ini_section=kwargs['ini_section']
            params = read_config_file(ini_section=self.ini_section)
            if self.conn is not None:
                self.conn.close()
            self.conn = psycopg2.connect(**params)
            cur = self.conn.cursor()
            if 'schema' in kwargs:
                self.schema=kwargs['schema']
            cur.execute(f"SET search_path='{self.schema}';")
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.conn = None
        finally:
            cur.close()
            return self
    def restartConnection(self,**kwargs):
        # recursively try to restart the connection to database.
        attempt=kwargs['attempt']
        if 'attlim' in kwargs:
            attlim =kwargs['attlim']
        else:
            attlim=self.MAX_CONNECTION_ATTEMPTS
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
            cur = self.conn.cursor()
            cur.execute(sql,(*args,))
            out=cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            if self.testConnection() == False:
                if self.restartConnection() == 'Connection re-established.':
                    return self.fetchone(sql,*args)
            else:
                print(error)
                return (error,)
        finally:
            cur.close()
            return out


    def fetchall(self,sql,*args):
        # returns a list of tuples
        # does not commit
        try:
            cur = self.conn.cursor()
            cur.execute(sql,(*args,))
            all =cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            if self.testConnection() == False:
                if self.restartConnection() == 'Connection re-established.':
                    return self.fetchall(sql,*args)
            else:
                print(error)
                return [(error,)]
        finally:
            cur.close()
            return all

    def testConnection(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1")
            back = cur.fetchone()[0]
        except:
            back = 0
        finally:
            cur.close()
            return back
if __name__ == "__main__":
    db = DBI(ini_section='local_launcher')
    print('is connected: ',db.testConnection()==True)
    print(db.fetchall('select * from survey'))