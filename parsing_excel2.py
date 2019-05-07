""" Вторая версия парсера ексель документа для БД swimming_competitions"""
import pyodbc


driver_excel = '{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}'
location_excel = 'D:\\for SQL Server\\excel_person.xls'
excel_list = '[Лист1$]'
driver_sql = '{SQL Server}'
server_sql = 'DESKTOP-NE8ID00\\SQLSERVER'
database_sql = 'swimming_competitions'


connection_str_excel = "DRIVER={};DBQ={};".format(driver_excel, location_excel)
connection_str_sql_server = "Driver={}; Server={}; Database={};".format(driver_sql, server_sql, database_sql)
conn_excel = pyodbc.connect(connection_str_excel, autocommit=True)
cursor_excel = conn_excel.cursor()
select_from_excel_str = "Select * From {}".format(excel_list)
cursor_excel.execute(select_from_excel_str)
excel_file = cursor_excel.fetchall()
conn_sql_server = pyodbc.connect(connection_str_sql_server)
cursor_sql_server = conn_sql_server.cursor()

