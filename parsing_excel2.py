""" Вторая версия парсера эксель документа для БД swimming_competitions"""
import pyodbc


driver_excel = '{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}'
location_excel = 'D:\\for SQL Server\\copy2.xlsx'  # copy2.xlsx  excel_person2.xls
excel_list = '[Лист1$]'  # [ПРОТОКОЛ$] или [Лист1$]
driver_sql = '{SQL Server}'
server_sql = 'DESKTOP-NE8ID00\\SQLSERVER'
database_sql = 'swimming_competitions'
ranks = [None, '2юн', '1юн', '3', '2', '1', 'кмс', 'мс', 'мсмк', 'змс']
nambers_0_to_9 = '1234567890'


def edit_excel():  # Правка экселя, для правильной интерпритации значения столбцов НЕ РАБОТАЕТ!!!
    connection_str_excel = "DRIVER={};DBQ={};".format(driver_excel, location_excel)
    conn_excel = pyodbc.connect(connection_str_excel, autocommit=True, ReadOnly = 0)
    cursor_excel = conn_excel.cursor()   # insert into city (title_city) values ('{}'
    # sstr_list = tuple(('строка ' * 7).split())
    insert_str = "insert into {} (A, B, C, D, E, F, G) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                 "".format(excel_list, 'строка ')
    cursor_excel.execute(insert_str)
    conn_excel.close()





connection_str_excel = "DRIVER={};DBQ={};".format(driver_excel, location_excel)
conn_excel = pyodbc.connect(connection_str_excel, autocommit=True, MaxScanRows=8)
cursor_excel = conn_excel.cursor()
select_from_excel_str = "Select * From {}".format(excel_list)
cursor_excel.execute(select_from_excel_str)
excel_file = cursor_excel.fetchall()

connection_str_sql_server = "Driver={}; Server={}; Database={};".format(driver_sql, server_sql, database_sql)
conn_sql_server = pyodbc.connect(connection_str_sql_server)
cursor_sql_server = conn_sql_server.cursor()


def create_string_for_sql(dictionary, table_name):  # Принимает словарь и название таблицы. Формирует сторку для SQL
    count_key = len(dictionary)
    string_one = "isert into {} (".format(table_name)
    string_two = ")  values ("
    keys_and_values = tuple(dictionary.items())
    columns = [(str(k[0]) + ",") for k in keys_and_values]
    columns[-1] = columns[-1].rstrip(',')
    values = [("'" + str(k[1]) + "',") for k in keys_and_values]
    values[-1] = values[-1].rstrip(',')
    columns = ' '.join(columns)
    values = ' '.join(values)
    string_finish = string_one + columns + string_two + values + ")"
    return string_finish


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


def get_time_second(raw_time):  # Преобразует время для второго экселя
    raw_time = raw_time.replace(",", ".")
    raw_time = raw_time.replace(":", ".")
    if raw_time.count(".") == 2:
        raw_time = raw_time.replace(".", ":", 1)
    return raw_time


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
            if club == 'Латвия':
                keys[5] = 'country'
                club = 'LAT'
            values = (name[1], name[0], year, rank, city, club, time)
            result = {k: v for k, v in zip(keys, values) if v is not None}
            result.update(competition)
            result.update(event)
            results.append(result)
    return results


def parser_excel_second_type(excel_file):
    event = dict.fromkeys(['title_event', 'date_event', 'city_event', 'pool'])
    event['title_event'] = 'Протокол '
    competition = dict.fromkeys(['gender', 'distance', 'style', 'birth_year_comp', 'day_comp'])
    results = []
    i = 0
    payment_falg = True
    for string in excel_file:
        string = tuple(string)
        none = string.count(None)
        if none == 1 or none == 4 or none == 5 or none == 6 or none == 9:
            continue
        if none == 7 and i < 3:
            i += 1
            event['title_event'] += string[1]
            continue
        if payment_falg:  # Парсинг данных event
            before = event['title_event'].index('г.')
            title_event = event['title_event'][:before]
            event['title_event'] = event['title_event'].split(',')
            for element in event['title_event']:
                if 'г.' in element:
                    i = (element.index('г.') + 2)
                    event['city_event'] = element[i:]
                elif 'бассейн' in element:
                    pool = [n for n in element if n in nambers_0_to_9]
                    event['pool'] = int(''.join(pool))
            event_date = (str(event['title_event'][-2][:2]) + str(event['title_event'][-2][-8:])).split('.')
            event_date.reverse()
            event['date_event'] = '-'.join(event_date)
            event['title_event'] = title_event
            payment_falg = False
        if none == 8:  # Строки с днями и competitions
            string = string[1]
            if 'день' in string:
                competition['day_comp'] = string[:6]
                continue
            else:
                string = string.split()
                for j, v in enumerate(string, start=1):
                    if j == 1:
                        if v == 'Девушки' or v == 'Девочки':
                            competition['gender'] = 'Ж'
                        else:
                            competition['gender'] = 'М'
                        continue
                    elif j == 2:
                        if len(v) < 5:
                            competition['birth_year_comp'] = int(v)
                        elif len(v) == 8:
                            competition['birth_year_comp'] = int(v[:4])
                        else:
                            competition['birth_year_comp'] = int(v[5:9])
                        continue
                    if '0' in v:
                        nine = ('1234567890')
                        distance = [namber for namber in v if namber in nine]
                        competition['distance'] = int(''.join(distance))
                        break
                style = []
                if '0' not in string[-2]:
                    style.append(string[-2])
                style.append(string[-1])
                competition['style'] = ' '.join(style)
                continue
        if none > 3:
            continue
        name = string[1].split()
        year = int('20' + str(string[2]))
        city_club = string[3].split(',', 1)
        if 'Гомель' in city_club[0]:
            city = 'Гомель'
        else:
            city = city_club[0]
        if len(city_club) == 2:
            club = city_club[1]
        else:
            club = None
        country = string[4]
        if none == 3:
            time = None
        else:
            time = get_time_second(string[5])
        if string[6] is None:
            points = None
        else:
            points = int(string[6])
        keys = ['firstname', 'lastname', 'birth_year', 'country', 'city', 'club', 'time', 'points']
        values = (name[1], name[0], year, country, city, club, time, points)
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
            # print(str_error)
        conn_sql_server.commit()
        primary_right += 1


def insert_gender():
    gender_list = ('М', 'Ж')
    for gender in gender_list:
        insert_gender_str = "insert into gender (title_gender) values ('{}')".format(gender)
        try:
            cursor_sql_server.execute(insert_gender_str)
        except (pyodbc.IntegrityError):
            str_error = "Ошибка при добовлении title_gender '{}' в таблицу gender!".format(gender)
            # print(str_error)
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
            # print(str_error)
        conn_sql_server.commit()


def insert_country(results):  # Таблица country
    countries = {result['country'] for result in results if 'country' in result}
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
                update_str = "update city set country_id = '{}' where title_city = '{}'".format(answer, city)
                cursor_sql_server.execute(update_str)
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
                # print(str_error)
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
            try:
                cursor_sql_server.execute(insert_str)
            except (pyodbc.IntegrityError):
                str_error = "Ошибка при добовлении event '{}', '{}', '{}', '{}' в таблицу" \
                            " event!".format(event[0], event[1], city_id, event[3])
                # print(str_error)
            conn_sql_server.commit()


def insert_competition(results):  # competition_id, gender_id, distance, style_id, birth_year, event_id, day
    t = 'title_event'
    d = 'date_event'
    year = 'birth_year_comp'
    competitions = {(r['gender'], r['distance'], r['style'], r[year], r['day_comp'], r[t], r[d]) for r in results}
    competitions = list(competitions)
    # [('Ж', 100, 'в/ст', 2006, 3)
    if len(competitions):
        for comp in competitions:
            select_str = "select gender_id from gender where title_gender='{}'".format(comp[0])
            cursor_sql_server.execute(select_str)
            gender_id = cursor_sql_server.fetchone()[0]
            select_str = "select style_id from style where title_style='{}'".format(comp[2])
            cursor_sql_server.execute(select_str)
            style_id = cursor_sql_server.fetchone()[0]
            sel_str = "select event_id from event where title_event='{}' and date_event='{}'".format(comp[5], comp[6])
            cursor_sql_server.execute(sel_str)
            event_id = cursor_sql_server.fetchone()[0]
            insert_str = "insert into competition (gender_id, distance, style_id, birth_year, event_id, day) " \
                         "values ('{}', '{}', '{}', '{}', '{}', '{}'" \
                         ")".format(gender_id, comp[1], style_id, int(comp[3]), event_id, comp[4])
            try:
                cursor_sql_server.execute(insert_str)
            except (pyodbc.IntegrityError):
                str_error = "Ошибка при добовлении competition '{}', '{}', '{}', '{}', '{}', '{}' в таблицу" \
                            " competition!".format(gender_id, comp[1], style_id, comp[3], event_id, comp[4])
                print(str_error)
            conn_sql_server.commit()


def insetr_person(results):  # firstname, lastname, gender_id, birth_year, rank_id, country_id, city_id, club_id
    f = 'firstname'
    l = 'lastname'
    g = 'gender'
    b = 'birth_year'
    r = 'rank'
    cont = 'country'
    city = 'city'
    club = 'club'
    keys = (f, l, g, b, r, cont, city, club)
    presons = []
    for res in results:
        person = {key: res[key] for key in keys if key in res}
        presons.append(person)
    i_error = 0  # Счетчик ошибок insert
    for person in presons:
        person_key = ['firstname', 'lastname', 'birth_year', 'gender_id']
        select_str = "select gender_id from gender where title_gender='{}'".format(person['gender'])
        cursor_sql_server.execute(select_str)
        gender_id = cursor_sql_server.fetchone()[0]
        person_values = [person['firstname'], person['lastname'], person['birth_year'], gender_id]
        if 'rank' in person:
            person_key.append('rank_id')
            select_str = "select rank_id from rank where rank_value='{}'".format(person['rank'])
            cursor_sql_server.execute(select_str)
            rank_id = cursor_sql_server.fetchone()[0]
            person_values.append(rank_id)
        if 'country' in person:
            person_key.append('country_id')
            select_str = "select country_id from country where abbreviation ='{}'".format(person['country'])
            cursor_sql_server.execute(select_str)
            country_id = cursor_sql_server.fetchone()[0]
            person_values.append(country_id)
        if 'city' in person:
            person_key.append('city_id')
            select_str = "select city_id from city where title_city ='{}'".format(person['city'])
            cursor_sql_server.execute(select_str)
            city_id = cursor_sql_server.fetchone()[0]
            person_values.append(city_id)
        if 'club' in person:
            person_key.append('club_id')
            select_str = "select club_id from club where title_club ='{}'".format(person['club'])
            cursor_sql_server.execute(select_str)
            club_id = cursor_sql_server.fetchone()[0]
            person_values.append(club_id)

        key_str = ', '.join(person_key)
        values_str = tuple(person_values)
        insert_str = "insert into person ({}) values {}".format(key_str, values_str)
        try:
            cursor_sql_server.execute(insert_str)
        except (pyodbc.IntegrityError):  # Если персон уже eсть, то пробуем обновить разряд
            i_error += 1
            if 'rank' in person:
                if 'club' in person:
                    sel = "select person_id, rank_id from person where {} ='{}'and {} ='{}'and {} ='{}' and {} ='{}'" \
                          " and {} ='{}'".format(person_key[0], person_values[0],
                                                 person_key[1], person_values[1],
                                                 person_key[2], person_values[2],
                                                 person_key[-2], person_values[-2],
                                                 person_key[-1], person_values[-1])
                else:
                    sel = "select person_id, rank_id from person where {} ='{}'and {} ='{}'and {} ='{}' and {} ='{}'" \
                          "".format(person_key[0], person_values[0],
                                    person_key[1], person_values[1],
                                    person_key[2], person_values[2],
                                    person_key[-1], person_values[-1])
                cursor_sql_server.execute(sel)
                row = cursor_sql_server.fetchone()
                person_id = int(row.person_id)
                old_rank_id = row.rank_id
                if old_rank_id is None:
                    primary_old_rank = 0
                else:
                    sel = "select primary_right from rank where rank_id = '{}'".format(old_rank_id)
                    cursor_sql_server.execute(sel)
                    primary_old_rank = int(cursor_sql_server.fetchone()[0])
                sel = "select primary_right, rank_id from rank where rank_value = '{}'".format(person['rank'])
                cursor_sql_server.execute(sel)
                row = cursor_sql_server.fetchone()
                primary_new_rank = int(row.primary_right)
                new_rank_id = int(row.rank_id)
                if primary_new_rank > primary_old_rank:
                    update_str = "update person set rank_id = '{}' where person_id = '{}'" \
                                 "".format(new_rank_id, person_id)
                    cursor_sql_server.execute(update_str)
        conn_sql_server.commit()


def insert_result(results):  # result_id, person_id, time, competition_id

    def select_city_id(title_city):  # Узнает city_id по названию города
        sel = "select city_id from city where title_city = '{}'".format(title_city)
        cursor_sql_server.execute(sel)
        row = cursor_sql_server.fetchone()
        city_id = int(row.city_id)
        return city_id

    def select_club_id(title_club):  # Узнает club_id по названию club
        sel = "select club_id from club where title_club= '{}'".format(title_club)
        cursor_sql_server.execute(sel)
        row = cursor_sql_server.fetchone()
        club_id = int(row.club_id)
        return club_id

    for result in results:
        if 'city' not in result and 'club' in result:
            club_id = select_club_id(result['city'])
            select = "select person_id from person where {} ='{}' and {} ='{}' and {} ='{}' and {} ='{}'" \
                     "".format('firstname', result['firstname'],
                               'lastname', result['lastname'],
                               'birth_year', result['birth_year'],
                               'club_id', club_id)
        elif 'city' in result and 'club' not in result:
            city_id = select_city_id(result['city'])
            select = "select person_id from person where {} ='{}' and {} ='{}' and {} ='{}' and {} ='{}'" \
                     "".format('firstname', result['firstname'],
                               'lastname', result['lastname'],
                               'birth_year', result['birth_year'],
                               'city_id', city_id)
        else:
            city_id = select_city_id(result['city'])
            club_id = select_club_id(result['club'])
            select = "select person_id from person where {} ='{}' and {} ='{}' and {} ='{}' and {} ='{}' and {} ='{}'" \
                     "".format('firstname', result['firstname'],
                               'lastname', result['lastname'],
                               'birth_year', result['birth_year'],
                               'city_id', city_id,
                               'club_id', club_id)
        cursor_sql_server.execute(select)  # Узнаем person_id
        person_id = int(cursor_sql_server.fetchone()[0])
        select_str = "select gender_id from gender where title_gender='{}'".format(result['gender'])
        cursor_sql_server.execute(select_str)
        gender_id = cursor_sql_server.fetchone()[0]
        select_str = "select style_id from style where title_style='{}'".format(result['style'])
        cursor_sql_server.execute(select_str)
        style_id = cursor_sql_server.fetchone()[0]
        select_str = "select event_id from event where title_event = '{}' and date_event = '{}'" \
                     "".format(result['title_event'], result['date_event'])
        cursor_sql_server.execute(select_str)
        event_id = cursor_sql_server.fetchone()[0]
        select = "select competition_id from competition where {} ='{}' and {} ='{}' and {} ='{}' and {} ='{}' and " \
                 "{} ='{}' and {} ='{}'".format('gender_id', gender_id,
                                                'distance', result['distance'],
                                                'style_id', style_id,
                                                'birth_year', result['birth_year_comp'],
                                                'day', result['day_comp'],
                                                'event_id', event_id)
        cursor_sql_server.execute(select)
        competition_id = int(cursor_sql_server.fetchone()[0])
        if 'time' in result:
            if
            insert_str = "insert into result (person_id, time, competition_id) values ('{}', '{}', '{}')" \
                        "".format(person_id, result['time'], competition_id)
        else:
            insert_str = "insert into result (person_id, competition_id) values ('{}', '{}')" \
                         "".format(person_id, competition_id)
        try:
            cursor_sql_server.execute(insert_str)
        except(pyodbc.IntegrityError):
            pass
            # print('Ошибка вставки результата в таблицу result!')
        conn_sql_server.commit()


if len(excel_file[0]) == 12:
    results = parser_excel_first_type(excel_file)
elif len(excel_file[0]) == 9:
    results = parser_excel_second_type(excel_file)
# insert_ranks(ranks)
# insert_gender()
# insert_style(results)
# insert_country(results)
# insert_city(results)
# insert_club(results)
# insert_event(results)
# insert_competition(results)
# insetr_person(results)
# insert_result(results)

conn_excel.close()
conn_sql_server.close()