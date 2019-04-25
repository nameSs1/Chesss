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


def rang_pars (rang_str):  # Прреобразует разряды к одному типу
    if rang_str is None:
        return None
    elif type(rang_str) is int:
        return str(rang_str)
    elif type(rang_str) is float:
        return str(int(rang_str))
    else:
        return rang_str


def parser_excel(excel_file):
    days = []  # Спиоск дней
    type_comp = []  # Список соревнований
    list_results = []  # Список результатов
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
            old_rang = rang_pars(string[3])
            new_rang = rang_pars(string[6])
            if old_rang not in list_rang:
                list_rang.append(old_rang)
            if new_rang not in list_rang:
                list_rang.append(new_rang)
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
            time = get_time(string[5])
            keys = ('name', 'surname', 'year', 'old_rang', 'new_rang', 'city', 'club', 'place', 'time', 'points', 'day', 'type')
            values = (surname, name, string[2], old_rang, new_rang, city, club, string[0], time, points, days[-1], type_comp[-1])
            sportsman = {k: v for k, v in zip(keys, values)}
            list_results.append(sportsman)
    return list_results, days, type_comp, list_rang


def remaining_tables(results):
    list_gender = ('male', 'famale')  # Список полов
    create_table_gender_str = 'create table table_gender (id_gender int primary key identity, gender varchar(10) unique)'
    try:
        cursor_sql_server.execute(create_table_gender_str)
    except (pyodbc.ProgrammingError):
        pass
    conn_sql_server.commit()
    for gender in list_gender:
        insert_table_gender_str = "insert into table_gender (gender) values ('{}')".format(gender)
        try:
            cursor_sql_server.execute(insert_table_gender_str)
        except (pyodbc.IntegrityError):
            pass
        conn_sql_server.commit()
    days = results[1]  # Таблица дней
    create_table_days_str = 'create table table_days (id_day int primary key identity, day nvarchar(10) unique)'
    try:
        cursor_sql_server.execute(create_table_days_str)
    except (pyodbc.ProgrammingError):
        print('Таблица table_days уже создана')
    conn_sql_server.commit()
    for day in days:
        insert_table_days_str = "insert into table_days (day) values ('{}')".format(day)
        try:
            cursor_sql_server.execute(insert_table_days_str)
        except(pyodbc.IntegrityError):
            pass
        conn_sql_server.commit()
    styles = [type_swim[1] for type_swim in results[2]]  # Список стилей плавонья
    styles = list(set(styles))
    create_table_styles_str = 'create table table_styles (id_style int primary key identity, style nvarchar(10) unique)'
    try:
        cursor_sql_server.execute(create_table_styles_str)
    except (pyodbc.ProgrammingError):
        print('Таблица table_styles уже создана')
    conn_sql_server.commit()
    for style in styles:
        insert_table_style_str = "insert into table_styles (style) values ('{}')".format(style)
        try:
            cursor_sql_server.execute(insert_table_style_str)
        except(pyodbc.IntegrityError):
            pass
        conn_sql_server.commit()
    type_comp = results[2]  # Таблица соревнований
    create_table_type_comp_str = 'create table type_comp (id_comp int primary key identity, distance int,' \
                                 ' style varchar(10), gender int, age int)'
    try:
        cursor_sql_server.execute(create_table_type_comp_str)
    except (pyodbc.ProgrammingError):
        print('Таблица type_comp уже создана')
    conn_sql_server.commit()
    for type in type_comp:
        if type[2] == 'девочки':
            gender = 'famale'
        elif type[2] == 'мальчики':
            gender = 'male'
        select_gender_table_type_comp_str = "select id_gender from table_gender where gender='{}'".format(gender)
        cursor_sql_server.execute(select_gender_table_type_comp_str)
        id_gender = cursor_sql_server.fetchone()[0]
        select_style_table_styles_comp_str = "select id_style from table_styles where style='{}'".format(type[1])
        cursor_sql_server.execute(select_style_table_styles_comp_str)
        style = cursor_sql_server.fetchone()[0]
        age = int(type[3][0:4])
        insert_table_type_comp_str = "insert into type_comp (distance, style, gender, age)" \
                                     "values ({}, '{}', {}, {})".format(type[0], style, id_gender, age)
        cursor_sql_server.execute(insert_table_type_comp_str)
        conn_sql_server.commit()
    list_rang = results[3]  # Список разрядов
    list_rang.remove(None)
    create_table_rangs_str = 'create table type_rangs (id_rang int primary key identity, rang varchar(4) unique)'
    try:
        cursor_sql_server.execute(create_table_rangs_str)
    except (pyodbc.ProgrammingError):
        print('Таблица type_rangs уже создана')
    conn_sql_server.commit()
    for rang in list_rang:
        insert_table_rangs_str = "insert into type_rangs (rang) values ('{}')".format(rang)
        try:
            cursor_sql_server.execute(insert_table_rangs_str)
        except (pyodbc.IntegrityError):
            pass
        conn_sql_server.commit()


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


results = parser_excel(excel_file)  # return list_results, days, type_comp, list_rang
# remaining_tables(results)
# insert_data(list_results)
conn_excel.close()
conn_sql_server.close()

