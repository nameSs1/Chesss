""" Третья версия парсера эксель документа для БД swimming_competitions"""
import pyodbc
import xlrd


location_excel = 'D:\\for SQL Server\\'
excel_name = 'excel_person2.xls'


def get_time_second(raw_time):  # Преобразует время для второго экселя
    raw_time = raw_time.replace(",", ".")
    raw_time = raw_time.replace(":", ".")
    if raw_time.count(".") == 2:
        raw_time = raw_time.replace(".", ":", 1)
    if (raw_time.index('.') + 2) == len(raw_time):
        raw_time += '0'
    if len(raw_time) == 5:
        raw_time = '00:00:' + raw_time
    else:
        raw_time = '00:0' + raw_time
    return raw_time


def parser_excel_second_type(excel_file):
    event = dict.fromkeys(['title_event', 'date_event', 'city_event', 'pool'])
    competition = dict.fromkeys(['gender', 'distance', 'style', 'birth_year_comp', 'day_comp'])
    results = []

    def parsing_event(string, i):  # Парсинг данных event
        if i == 0:
            event['title_event'] = string[1]
        elif i == 1 or i == 2:
            event['title_event'] += string[1]
        elif i == 3:
            event['city_event'] = string[1][string[1].index('г.') + 2:string[1].index(',')]
            event['pool'] = int(string[1][string[1].index('бассейн') + 7:string[1].index('м')])
            substring_date = string[1].split(',')
            event_date = (str(substring_date[2][:2]) + str(substring_date[2][-8:])).split('.')
            event_date.reverse()
            event['date_event'] = '-'.join(event_date)
        return event

    def parsing_competition(string):  # Парсим информацию о competition
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
                nine = '1234567890'
                distance = [namber for namber in v if namber in nine]
                competition['distance'] = int(''.join(distance))
                break
        style = []
        if '0' not in string[-2]:
            style.append(string[-2])
        style.append(string[-1])
        competition['style'] = ' '.join(style)

    def parsing_swimmer(string):  # Парсим информацию о плавце
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
        if empty_cells == 3:
            time = None
        else:
            time = get_time_second(str(string[5]))
        if string[6] == '':
            points = None
        else:
            points = int(string[6])
        keys = ['firstname', 'lastname', 'birth_year', 'country', 'city', 'club', 'time', 'points']
        values = (name[1], name[0], year, country, city, club, time, points)
        swimmer = {k: v for k, v in zip(keys, values) if v is not None}
        return swimmer

    for i in range(excel_file.nrows):
        string = excel_file.row_values(i)
        empty_cells = string.count('')  # Считает сколько пустых ячеек
        if empty_cells in (1, 4, 5, 6, 7, 9):  # Пустые строки, ничего не делаем
            continue
        elif empty_cells == 8 and i < 4:  # Узнаем информацию о мероприятии(event)
            parsing_event(string, i)
        elif empty_cells == 8 and 'день' in string[1]:  # Узнаем день соревнований
            competition['day_comp'] = int(string[1][:2])
        elif empty_cells == 8:  # Узнаем информацию о competition
            parsing_competition(string[1])
        elif string[0] != '':
            swimmer = parsing_swimmer(string)
            swimmer.update(competition)
            swimmer.update(event)
            results.append(swimmer)
    return results


def reading_excel(location_excel, excel_name):
    rb = xlrd.open_workbook(location_excel + excel_name, formatting_info=True)
    sheet = rb.sheet_by_index(0)
    if (sheet.ncols) == 9:
        return parser_excel_second_type(sheet)


# reading_excel(location_excel, excel_name)
for i in reading_excel(location_excel, excel_name):
    print(i)

