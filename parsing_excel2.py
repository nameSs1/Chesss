""" Вторая версия парсера эксель документа для БД swimming_competitions"""
import pyodbc


driver_excel = '{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}'
location_excel = 'D:\\for SQL Server\\excel_person.xls'
excel_list = '[Лист1$]'  # [ПРОТОКОЛ$] или [Лист1$]
driver_sql = '{SQL Server}'
server_sql = 'DESKTOP-NE8ID00\\SQLSERVER'
database_sql = 'swimming_competitions'
ranks = [None, '2юн', '1юн', '3', '2', '1', 'кмс', 'мс', 'мсмк', 'змс']


connection_str_excel = "DRIVER={};DBQ={};".format(driver_excel, location_excel)
connection_str_sql_server = "Driver={}; Server={}; Database={};".format(driver_sql, server_sql, database_sql)
conn_excel = pyodbc.connect(connection_str_excel, autocommit=True)
cursor_excel = conn_excel.cursor()
select_from_excel_str = "Select * From {}".format(excel_list)
cursor_excel.execute(select_from_excel_str)
excel_file = cursor_excel.fetchall()
conn_sql_server = pyodbc.connect(connection_str_sql_server)
cursor_sql_server = conn_sql_server.cursor()

# if len(excel_file[0]) == 12:
#     type_file = 1
# elif len(excel_file[0]) == 9:
#     type_file = 2

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


def parser_excel_first_type (excel_file):
    event = dict.fromkeys(['title_event', 'date_event', 'city_event', 'pool'])
    event['title_event'] = 'Итоговый протокол'
    competition = dict.fromkeys(['gender', 'distance', 'style', 'birth_year_comp', 'day_comp'])
    competition['day_comp'] = 1
    results = []
    i = 0
    for string in excel_file:
        i += 1
        if i == 1 or i == 2:
            event['title_event'] += string[0]
            continue
        elif i == 4:
            date_start = string[1][:2]  # Преобразавания даты в формат ГГГГ-ММ-ДД
            date_event = string[1][5:13]
            date_event = date_start + date_event
            date_event = date_event.split('.')
            date_event.reverse()
            date_event = '-'.join(date_event)
            event['date_event'] = date_event
            event['city_event'] = string[1][-7:]
            event['pool'] = int(string[6].split()[1])
            continue
        string = tuple(string)
        count_none = string.count(None)
        if count_none == 12 or count_none == 10 or i == 5:
            continue
        elif count_none == 11:
            string = [s for s in string if s is not None][0]
            if 'день' in string:
                competition['day_comp'] = int(string[0])
                continue
            else:
                list_comp = string.split()
                competition['distance'] = int(list_comp[0])
                competition['style'] = list_comp[1]
                if list_comp[2] == 'девочки':
                    competition['gender'] = 'Ж'
                else:
                    competition['gender'] = 'М'
                competition['birth_year_comp'] = int(list_comp[3])
                continue
        else:
            name = string[1].split()
            year = int(string[2])
            city_club = string[4].split(',', 1)
            city = city_club[0]
            if len(city_club) == 2:
                club = city_club[1].lstrip()
            else:
                club = None
            time = get_time(string[5])
            rank = rang_pars(string[3])
            new_rank = rang_pars(string[6])
            if ranks.index(rank) < ranks.index(new_rank):
                rank = new_rank
            keys = ['firstname', 'lastname', 'birth_year', 'rank', 'city', 'club', 'time']
            values = (name[1], name[0], year, rank, city, club, time)
            if club == 'Латвия':
                keys[5] = 'country'
                club = 'LAT'
            result = {k: v for k, v in zip(keys, values) if v is not None}
            result.update(competition)
            result.update(event)
            results.append(result)
    return results


def insert_ranks(ranks):  # Таблица rank, колонка rank_value, primary_right
    primary_right = 0
    for rank in ranks:
        insert_rank_str = "insert into rank (rank_value, primary_right) values ('{}', '{}')".format(rank, primary_right)
        try:
            cursor_sql_server.execute(insert_rank_str)
        except (pyodbc.IntegrityError):
            str_error = "Ошибка при добовлении разряда {} в таблицу rank!".format(rank)
            print(str_error)
        conn_sql_server.commit()
        primary_right += 1


def insert_gender():
    gender_list = ('М', 'Ж')
    for gender in gender_list:
        insert_gender_str = "insert into gender (gender) values ('{}')".format(gender)
        try:
            cursor_sql_server.execute(insert_gender_str)
        except (pyodbc.IntegrityError):
            str_error = "Ошибка при добовлении gender '{}' в таблицу gender!".format(gender)
            print(str_error)
        conn_sql_server.commit()


def insert_style(results):  # Таблица style, колонка title_style
    styles = {result['style'] for result in results}
    styles = list(styles)
    for style in styles:
        insert_style_str = "insert into style (title_style) values ('{}')".format(style)
        try:
            cursor_sql_server.execute(insert_style_str)
        except (pyodbc.IntegrityError):
            str_error = "Ошибка при добовлении title_style '{}' в таблицу style!".format(style)
            print(str_error)
        conn_sql_server.commit()


def insert_country(results):  # Таблица country
    countries = {result['country'] for result in results}
    if len(countries) != 0:
        countries = list(countries)
        for country in countries:
            select_str = "select * from country where abbreviation='{}'".format(country)
            cursor_sql_server.execute(select_str)
            answer = cursor_sql_server.fetchone()  # Узнаем есть ли страна в таблице country
            if answer is None:  # Если страны нет, то вставляем ее
                insert_str = "insert into country (abbreviation) values ('{}')".format(country)
                cursor_sql_server.execute(insert_str)
                conn_sql_server.commit()


def insert_city(results):  # Таблица city , колонки title_city и country_id
    cityes = {result['city'] for result in results}
    cityes = list(cityes)
    for city in cityes:
        select_str = "select * from city where title_city='{}'".format(city)
        cursor_sql_server.execute(select_str)
        answer = cursor_sql_server.fetchone()  # Узнаем есть ли город в таблице city
        if answer is not None:  # Если город есть, то узнаем есть ли ссылка на страну
            select_str = "select country_id from city where title_city='{}'".format(city)
            cursor_sql_server.execute(select_str)
            answer = cursor_sql_server.fetchone()
            if answer is not None:
                continue
            else:
                country = None  # Если город есть, но нет страны, то пробуем узнать ее
                for result in results:
                    if 'country' in result:
                        if result['city'] == city:
                            country = result['country']
                            break
                if country is None:
                    continue
                else:  # Если можем добавить страну
                    select_str = "select country_id from country where abbreviation='{}'".format(country)
                    cursor_sql_server.execute(select_str)
                    answer = cursor_sql_server.fetchone()[0]
                    insert_str = "insert into city (country_id) values ('{}')".format(answer)
                    cursor_sql_server.execute(insert_str)
                    conn_sql_server.commit()
                    continue
        else:  # Если города в списке нет, то добовляем
            insert_str = "insert into city (title_city) values ('{}')".format(city)
            cursor_sql_server.execute(insert_str)
            conn_sql_server.commit()
            country = None  # Теперь пробуем добавить индекс страны
            for result in results:
                if 'country' in result:
                    if result['city'] == city:
                        country = result['country']
                        break
            if country is None:
                continue
            else:  # Если можем добавить страну, то добовляем
                select_str = "select country_id from country where abbreviation='{}'".format(country)
                cursor_sql_server.execute(select_str)
                answer = cursor_sql_server.fetchone()[0]
                insert_str = "insert into city (country_id) values ('{}')".format(answer)
                cursor_sql_server.execute(insert_str)
                conn_sql_server.commit()
                continue


def insert_club(results):  # Таблица club, колонки title_club и city_id
    clubs = {(result['club'], result['city']) for result in results if 'club' in result}
    clubs = list(clubs)
    if len(clubs):
        for club in clubs:
            select_str = "select city_id from city where title_city='{}'".format(club[1])
            cursor_sql_server.execute(select_str)
            answer = cursor_sql_server.fetchone()[0]
            insert_str = "insert into club (title_club, city_id) values ('{}', '{}')".format(club[0], answer)
            try:
                cursor_sql_server.execute(insert_str)
            except (pyodbc.IntegrityError):
                str_error = "Ошибка при добовлении club '{}' в таблицу club!".format(club[0])
                print(str_error)
            conn_sql_server.commit()


def insert_event(results):  # Таблица event, колонки title_event, date_event, city_id, pool
    events = {(result['title_event'], result['date_event'], result['city_event'], result['pool']) for result in results}
    events = list(events)
    # [('Итоговы ... ти Героя Советского Союза М.Ф.Шмырёва', '2019-04-10', 'Витебск', 25)]
    if len(events):
        for event in events:
            select_str = "select city_id from city where title_city='{}'".format(event[2])
            cursor_sql_server.execute(select_str)
            answer = cursor_sql_server.fetchone()
            if answer is None:
                insert_str = "insert into city (title_city) values ('{}')".format(event[2])
                cursor_sql_server.execute(insert_str)
                conn_sql_server.commit()
                select_str = "select city_id from city where title_city='{}'".format(event['city_event'])
                cursor_sql_server.execute(select_str)
                answer = cursor_sql_server.fetchone()
                city_id = answer[0]
            else:
                city_id = answer[0]
            insert_str = "insert into event (title_event, date_event, city_id, pool) values ('{}', '{}', '{}', '{}'" \
                         ")".format(event[0], event[1], city_id, event[3])
            cursor_sql_server.execute(insert_str)
            conn_sql_server.commit()

























results = parser_excel_first_type (excel_file)
# insert_style(results)
# insert_city(results)
# insert_club(results)
# insert_event(results)