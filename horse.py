import tkinter

x_start=1
y_start=1
x_end=None
y_end=None


def bust_moves(x_start, y_start): #перебор ходов для фигруры
    xy_end = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)] # список возможных ходов
    moves=[]  # Список возможных ходов после проверки
    eight = (1,2,3,4,5,6,7,8)
    for xy in xy_end:
        new_x = x_start + xy[0]
        new_y = y_start + xy[1]
        if new_x and new_y in eight:
            moves.append((new_x,new_y))

    return moves

def way_figure( x_start, y_start, type_figure, x_finish, y_finish): #вычисляет путь фигуры от А к Б
    i = 0 # счетчик цикла while
    flag_found_way = False # флаг нахождения кратчайшего пути
    short_way = [[(x_start, y_start )]]
    passed_cell = set() # Пройденые клетки
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

