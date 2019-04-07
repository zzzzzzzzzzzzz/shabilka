# coding=utf-8
import pymysql

from init import config as conf

if __name__=='__main__':
    with pymysql.connect(conf.DB_HOST, conf.DB_USER, conf.DB_USER_PASSWORD, conf.DB_NAME) as cursor:

        # execute SQL query using execute() method.
        cursor.execute("SELECT VERSION()")

        # Fetch a single row using fetchone() method.
        data = cursor.fetchone()
        print(data)
        print("Database version : %s " % data)