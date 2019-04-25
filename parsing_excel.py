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
            values = (surname, name, int(string[2]), old_rang, new_rang, city, club, string[0], time, points, days[-1], type_comp[-1])
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
    create_table_type_comp_str = 'create table table_comp (id_comp int primary key identity, distance int,' \
                                 ' style varchar(10), gender int, age int)'
    try:
        cursor_sql_server.execute(create_table_type_comp_str)
    except (pyodbc.ProgrammingError):
        print('Таблица table_comp уже создана')
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
        insert_table_table_comp_str = "insert into table_comp (distance, style, gender, age)" \
                                     "values ({}, '{}', {}, {})".format(type[0], style, id_gender, age)
        cursor_sql_server.execute(insert_table_table_comp_str)
        conn_sql_server.commit()
    list_rang = results[3]  # Список разрядов
    list_rang.remove(None)
    create_table_rangs_str = 'create table table_rangs (id_rang int primary key identity, rang varchar(4) unique)'
    try:
        cursor_sql_server.execute(create_table_rangs_str)
    except (pyodbc.ProgrammingError):
        print('Таблица table_rangs уже создана')
    conn_sql_server.commit()
    for rang in list_rang:
        insert_table_rangs_str = "insert into table_rangs (rang) values ('{}')".format(rang)
        try:
            cursor_sql_server.execute(insert_table_rangs_str)
        except (pyodbc.IntegrityError):
            pass
        conn_sql_server.commit()


def insert_data(list_results):  # Обработка данных полученых из Excel
    lambda_gender = lambda string: 'famale' if string == 'девочки' else 'male'
    create_table_sportsmans_str = 'create table sportsmans (id int primary key identity, name varchar(20),' \
                                 ' surname varchar(20), gender int, year int, city varchar(20), club varchar(20))'
    create_table_results_str = 'create table results (id_sportsman int, place smallint, time time(2),' \
                               'points tinyint, old_rang tinyint, new_rang tinyint, day smallint, distance smallint,' \
                               'style tinyint, gender tinyint, age smallint)'
    try:
        cursor_sql_server.execute(create_table_sportsmans_str)
    except (pyodbc.ProgrammingError):
        print('Таблица sportsmans уже создана')
    conn_sql_server.commit()
    try:
        cursor_sql_server.execute(create_table_results_str)
    except (pyodbc.ProgrammingError):
        print('Таблица results уже создана')
    conn_sql_server.commit()
    sportsmans = [(man['name'], man['surname'], man['type'][2], int(man['year']), man['city'], man['club']) for man in list_results]
    sportsmans = list(set(sportsmans))
    for person in sportsmans:
        gender_str = "select id_gender from table_gender where gender = '{}'".format(lambda_gender(person[2]))
        cursor_sql_server.execute(gender_str)
        gender = cursor_sql_server.fetchone()[0]
        person_str = "insert into sportsmans (name, surname, gender, year, city, club) values ('{}', '{}', '{}'," \
                     " '{}', '{}', '{}')".format(person[0], person[1], gender, person[3], person[4], person[5])
        try:
            cursor_sql_server.execute(person_str)
        except(pyodbc.IntegrityError):
            pass
        conn_sql_server.commit()
    for r in list_results:
        str_select_person = "select id from sportsmans where name='{}' and surname='{}' and year='{}' and" \
                            " city='{}'".format(r['name'], r['surname'], int(r['year']), r['city'])
        cursor_sql_server.execute(str_select_person)
        id_sportsman = cursor_sql_server.fetchone()[0]
        if r['old_rang'] is not None:
            str_old_rang = "select id_rang from table_rangs where rang='{}'".format(r['old_rang'])
            cursor_sql_server.execute(str_old_rang)
            id_old_rang = cursor_sql_server.fetchone()[0]
        else:
            id_old_rang = None
        if r['new_rang'] is not None:
            str_new_rang = "select id_rang from table_rangs where rang='{}'".format(r['new_rang'])
            cursor_sql_server.execute(str_new_rang)
            id_new_rang = cursor_sql_server.fetchone()[0]
        else:
            id_new_rang = None
        str_day = "select id_day from table_days where day='{}'".format(r['day'])
        cursor_sql_server.execute(str_day)
        id_day = cursor_sql_server.fetchone()[0]
        str_style = "select id_style from table_styles where style='{}'".format(r['type'][1])
        cursor_sql_server.execute(str_style)
        id_style = cursor_sql_server.fetchone()[0]
        str_gender = "select id_gender from table_gender where gender='{}'".format(lambda_gender(r['type'][2]))
        cursor_sql_server.execute(str_gender)
        id_gender = cursor_sql_server.fetchone()[0]
        age = int(r['type'][3][0:4])
        values = (id_sportsman, id_old_rang, id_new_rang, r['place'], r['time'], r['points'], id_day, int(r['type'][0]), id_style, id_gender, age)
        name_key = ('id_sportsman', 'old_rang', 'new_rang', 'place', 'time', 'points', 'day', 'distance', 'style', 'gender', 'age')
        dict_r = {k: v for (k, v) in zip(name_key, values) if v is not None}
        keys_r = list(dict_r.keys())
        keys_r = ', '.join(keys_r)
        values_str = tuple(dict_r.values())
        insert_str = "insert into results ({}) values {}".format(keys_r, values_str)
        cursor_sql_server.execute(insert_str)
        conn_sql_server.commit()


results = parser_excel(excel_file)  # return list_results, days, type_comp, list_rang
remaining_tables(results)
insert_data(results[0])
conn_excel.close()
conn_sql_server.close()

