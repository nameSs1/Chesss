import tkinter

x_start=2
y_start=4
x_end=None
y_end=None

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

def logic_figure_horse( x_start, y_start, x_end, y_end): # логика поведения фигры "КОНЬ"
    if abs(x_end-x_start) == 2 and abs(y_end-y_start) == 1:
        flag=True
    elif abs(x_end-x_start) == 1 and abs(y_end-y_start) == 2:
        flag=True
    else:
        flag=False
    return flag

def way_figure( x_start, y_start, type_figure, x_finish, y_finish): #вычисляет путь фигуры от А к Б
    flag_found_way = False # флаг нахождения кратчайшего пути
    short_way = [[x_start, y_start, 1,[]]] #кратчайший путь, [2]: 0-свободна, 1-занята своим, 2 - занята чужим
    passed_cell = [] # Пройденые клетки          четвертый параметр -- индекс клетки для поиска удачного пути
    last_cell = [] # Последняя клетка
    i = 0
    while flag_found_way == False:
        # if x_finish == short_way[i][0] and y_finish == short_way[i][1]: # для прохода по всем клеткам один раз --- ВЫКЛ
        if len(short_way[i][3]) == 63:    # для прохода по всем клеткам один раз --- ВКЛ
            flag_found_way = True
            last_cell = short_way[i]
            continue
        b =  bust_moves(short_way[i][0],short_way[i][1])
        for a in b:
            # if a in short_way: # для прохода по всем клеткам один раз --- ВКЛ
            #     b.remove(a)
            for sublis in short_way: # для прохода по всем клеткам один раз --- ВКЛ
                if sublis[0:1] == a:
                    b.remove(a)
                    continue
            if a == False:
                continue
            else:
                a.extend([0, []])
                a[3].extend(short_way[i][3])
                a[3].extend([a[0], a[1]])
        short_way.extend(b)
        i+=1
    i=1
    for c in last_cell[3][::]:
        if i%2!=0:
            passed_cell.append([c])
        else:
            passed_cell[int(i/2)-1].extend([c])
        i+=1

    return passed_cell

print(way_figure(x_start, y_start, 1, x_end, y_end))


# indices = [i for i, x in enumerate(my_list) if x == "whatever"]