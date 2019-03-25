import tkinter

x_start=1
y_start=1
x_end=None
y_end=None



def logic_figure_horse( x_start, y_start, x_end, y_end): # логика поведения фигры "КОНЬ"
    if abs(x_end-x_start) == 2 and abs(y_end-y_start) == 1:
        flag=True
    elif abs(x_end-x_start) == 1 and abs(y_end-y_start) == 2:
        flag=True
    else:
        flag=False
    return flag

def bust_moves(x_start, y_start): #перебор ходов для фигруры
    x_end,y_end = range(1,9),range(1,9)
    moves=[]  # Список возможных ходов
    not_moves = []
    for x in x_end:
        for y in y_end:
            if logic_figure_horse(x_start, y_start, x, y) == True:
                moves.append([x, y])
            else:
                not_moves.append([x, y])
            y+=1
        x+=1
    return moves

def way_figure( x_start, y_start, type_figure, x_finish, y_finish): #вычисляет путь фигуры от А к Б
    i = 0 # счетчик цикла while
    flag_found_way = False # флаг нахождения кратчайшего пути
    short_way = [[(x_start, y_start )]]
    passed_cell = set() # Пройденые клетки          четвертый параметр - индекс клетки для поиска удачного пути
    last_cell = [] # Последняя клетка
    tuple_finish = (x_finish, y_finish)
    len_short = 1
    while flag_found_way == False:
        # if tuple_finish in short_way[i]:  # Для нахождения пути от клетки к клетке
        if len(short_way[i]) > len_short:    # Для задачи с конем
            len_short = len(short_way[i])     # Для задачи с конем
            print(len_short)                   # Для задачи с конем
        if len(short_way[i]) > 63: # Для задачи с конем
            flag_found_way = True
            last_cell = short_way[i]
            continue
        b =  bust_moves(short_way[i][-1][0],short_way[i][-1][1])
        for a in b:
            a = tuple(a)
            if a in short_way[i]:
                continue
            else:
                new_list = short_way[i].copy()
                new_list.append(a)
                short_way.append(new_list)



        i+=1
    return last_cell

print(way_figure(x_start, y_start, 1, x_end, y_end))

