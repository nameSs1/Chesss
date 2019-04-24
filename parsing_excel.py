import pyodbc


connectionstring_excel = str(
    r'DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};'
    r'DBQ=D:\for SQL Server\excel_person.xls;')
conn_excel = pyodbc.connect(connectionstring_excel, autocommit=True)
cursor_excel = conn_excel.cursor()
cursor_excel.execute('Select * From [Лист1$]')
excel_file = cursor_excel.fetchall()


connectionstring_sql_server = ('Driver={SQL Server}; Server=DESKTOP-NE8ID00\\SQLSERVER;  Database=swimming competition;')
conn_sql_server = pyodbc.connect(connectionstring_sql_server)
cursor_sql_server = conn_sql_server.cursor()


def get_time(string):
    if string != 'дисквал.':
        string = list(string)
        i = string.index('.')
        string[i] = ':'
        i = string.index(',')
        string[i] = '.'
        string = ''.join(string)
        return '00:' + string
    else:
        return None


def parser_excel(excel_file):
    days = []  # Спиоск дней
    type_comp = []  # Список соревнований
    list_results= []  # Список результатов
    list_rang = []  # Список разрадов
    for i, string in enumerate(excel_file, start=1):
        count_none = 0
        for element in string:
            if element is None:
                count_none += 1
            elif type(element) is str:
                if 'день' in element:
                    days.append(element)
                elif 'мальчики' in element or 'девочки' in element:
                    type_comp.append(element.split(maxsplit=3))
                else:
                    pass
        if count_none < 8 and string[0] != '№':  # Отсеиваются не нужные строки
            old_name = string[1].split()
            name = old_name[0]
            surname = old_name[1]
            if string[3] not in list_rang:
                list_rang.append(string[3])
            if string[6] not in list_rang:
                list_rang.append(string[6])
            city_club = string[4].split(',', 1)
            city = city_club[0]
            if len(city_club) == 2:
                club = city_club[1]
            else:
                club = None
            if string[7] is not None and string[7] != 'в.к.':
                points = int(string[7])
            elif string[8] is not None and string[8] != 'в.к.':
                points = int(string[8])
            else:
                points = None
            sportsman = [
                i,  # id Результата
                name,  # Имя
                surname,  # Фамилия
                string[2],  # Год рождения
                string[3],
                string[6],
                city,  # Город
                club,  # Клуб, если есть. Если нет -- None
                string[0],  # Место
                string[5],  # Результат
                points,  # Очки
                days[-1],  # День соревнований
                type_comp[-1]  # Тип соревнований
            ]
            list_results.append(sportsman)

    return list_results

list_results = parser_excel(excel_file)


def insert_data(list_results):  # Обработка данных полученых из Excel
    # Сущность "спортсмен"  id, name, surname, year, city, club
    # Сущность "результаты" id(спортсмена), old and new rangs, время, очки, ссылка на вид соревнования(id)

    sportsman = [(man[1], man[2], int(man[3]), man[6], man[7]) for man in list_results]
    sportsman = list(set(sportsman))
    # for i in list_results:
    #     print(i)
    # for man in sportsman:
    #     cursor_sql_server.execute(
    #         f"insert into sportsmans(name, surname, age, city, club)"
    #         f"values ('{man[1]}', '{man[0]}', {man[2]}, '{man[3]}', '{man[4]}')")
    #     conn_sql_server.commit()
    for r in list_results:
        cursor_sql_server.execute(
            f"select id from sportsmans "
            f"where name = '{r[2]}' and surname = '{r[1]}' and age = {int(r[3])} and city = '{r[6]}'")
        id_sportsman = cursor_sql_server.fetchone()
        id_sportsman = id_sportsman[0]
        r = [id_sportsman, r[4], r[5], r[8], r[9], r[10], r[11], r[12]]
        r[4] = get_time(r[4])
        end_r = r.pop()
        r.extend(end_r)
        name_key = ('sportsman', 'old_rang', 'new_rang', 'place', 'time', 'points', 'day', 'distance', 'style', 'gender', 'age')
        dict_r = {k: v for (k, v) in zip(name_key, r) if v is not None}
        keys_r = list(dict_r.keys())
        keys_r = ', '.join(keys_r)
        values_str = tuple(dict_r.values())
        insert_str = "insert into results ({}) values {}".format(keys_r, values_str)
        cursor_sql_server.execute(insert_str)
        conn_sql_server.commit()




insert_data(list_results)
conn_excel.close()
conn_sql_server.close()

