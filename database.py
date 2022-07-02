from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, MetaData, JSON


SQLITE = 'sqlite'

# Table Names
AIRDROPS = 'airdrops'

class AirdropDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None
    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.lower()
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            print("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        metadata = MetaData()
        Table(AIRDROPS, metadata,
            Column('id', Integer, primary_key=True),
            Column('data', JSON),
        )

        try:
            metadata.create_all(self.db_engine, checkfirst=True)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)
    
    def execute_query(self, query=''):
        if query == '' : return
        print (query)
        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
            except Exception as e:
                print(e)
    
    def get_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format(table)
        print(query)
        with self.db_engine.connect() as connection:
            try:
                db_data = []
                result = connection.execute(query)
                for row in result:
                    db_data.append(row)    
                result.close()
                return db_data
            except Exception as e:
                print(e)
            
              
        print("\n")