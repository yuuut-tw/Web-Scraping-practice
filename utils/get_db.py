
import pandas as pd
import mysql.connector


def delete_table(client, database, table, date_list, where=None):
    database = database.replace('`','')
    try:
        date_list = [ f"'{x}'" for x in date_list]
        con = mysql.connector.connect(
            host=client["host"],
            user=client["user"],
            password=client["pwd"],
            database=database,
            auth_plugin='mysql_native_password'
        )
        cursor = con.cursor(buffered=True)
        del_sql = f'''
            DELETE 
            FROM
            	`{database}`.`{table.replace('`','')}` 
            WHERE
            	`date` in ({', '.join(date_list)}) 
        '''
        if where != None:
            del_sql = del_sql + ' ' + where
        cursor.execute(del_sql)
        con.commit()
        res = f'success : delete {database}.{table}'
    except Exception as e:
        res = f'failed : delete {database}.{table}'
        print(e)
        error = e
    finally:
        cursor.close()
        con.close()
        print(res)
        if 'failed' in res:
            raise Exception(error)
        return res
    


def delete_whole_table(client, database, table):
    database = database.replace('`','')
    try:

        con = mysql.connector.connect(
            host=client["host"],
            user=client["user"],
            password=client["pwd"],
            database=database,
            auth_plugin='mysql_native_password'
        )
        cursor = con.cursor(buffered=True)
        del_sql = f'''
            DELETE 
            FROM
            	`{database}`.`{table.replace('`','')}`
        '''

        cursor.execute(del_sql)
        con.commit()
        res = f'success : delete whole {database}.{table}'
    except Exception as e:
        res = f'failed : delete whole {database}.{table}'
        print(e)
        error = e
    finally:
        cursor.close()
        con.close()
        print(res)
        if 'failed' in res:
            raise Exception(error)
        return res
    


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

