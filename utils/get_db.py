
import pandas as pd
import mysql.connector



def write_table(client, database, table, col, df):
    
    database = database.replace('`','')
    if len(df)<1:
        return 'empty data'
    
    df = df.where(pd.notnull(df), None)
    try:
        col = [ f'`{x}`' for x in col]
        con = mysql.connector.connect(
            host=client['host'],
            user=client['user'],
            password=client['pwd'],
            database=database,
            auth_plugin='mysql_native_password'
        )
        cursor = con.cursor(buffered=True)
        
        s = ['%s'] * len(col)  #  col數量
        insert_sql = f'''
            INSERT INTO `{database}`.`{table.replace('`','')}`
                ({', '.join(col)})
            VALUES
                ({', '.join(s)})
        '''
        if len(df)>1:
            values = df.values.tolist()
            for i in range(1+len(values)//10000):
                cursor.executemany(insert_sql, values[i*10000:(i+1)*10000])
                con.commit()
        else:
            for val in df.values:
                val = tuple(val)
                cursor.execute(insert_sql, val)
            con.commit()
            
        res = f'success : insert {database}.{table}'
    except Exception as e:
        con.rollback()
        res = f'failed : insert {database}.{table}'
        print(e)
        error = e
    finally:
        cursor.close()
        con.close()
        print(res)
        if 'failed' in res:
            raise Exception(error)
        return res

