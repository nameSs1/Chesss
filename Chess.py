import tkinter


def way_figure( x_start, y_start, type_figure, x_finish, y_finish): #вычисляет путь фигуры от А к Б
    flag_found_way = False # флаг нахождения кратчайшего пути
    short_way = [[x_start, y_start, 0,[]]] #кратчайший путь, [2]: 0-свободна, 1-занята своим, 2 - занята чужим
    passed_cell = [] # Пройденые клетки          четвертый параметр -- индекс клетки для поиска удачного пути
    last_cell = [] # Последняя клетка
    i = 0
    while flag_found_way == False:
        if x_finish == short_way[i][0] and y_finish == short_way[i][1]:
            flag_found_way = True
            last_cell = short_way[i]
            continue
        b =  bust_moves(short_way[i][0],short_way[i][1])
        for a in b:
            if a in short_way: # для прохода по всем клеткам один раз --- ВКЛ
                b.remove(a)
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


def xy_figure(x ,y , type_figure, size=1): # вычисление координат фигур
    if type_figure == 1: #считает координаты фигуры "КОНЬ"
        xy_horse = (
        [9, 47], [39, 47], [39, 44], [37, 44], [37, 44], [37, 40], [34, 40], [33, 36], [32, 33], [32, 28], [34, 25],
        [35, 24], [38, 24], [39, 20], [39, 16], [38, 11], [37, 9], [36, 7], [34, 5], [32, 4], [30, 3], [28, 3],
        [25, 3], [21, 3], [18, 4], [16, 6], [19, 9], [10, 19], [14, 24], [18, 22], [22, 19], [26, 19], [27, 17],
        [26, 19], [24, 19], [19, 29], [16, 34], [15, 36], [14, 40], [11, 40], [11, 44], [9, 44], [9, 47])
        for xy in xy_horse:
            xy[0] = xy[0] * size + 40 + (x - 1) * 50 * size  # x_start позиция фигуры от 1 до 8
            xy[1] = xy[1] * size + 40 + (y - 1) * 50 * size  # y_start позиция фигуры от 1 до 8
        return xy_horse

def draw_figure( x, y, type_figure, callor_figure): # рисует фигуры
    p.create_polygon(xy_figure( x, y, type_figure), fill = callor_figure, outline='black')
    # p.create_polygon(xy_figure(x_start,y_start), fill='white', outline='black')
    # for i in bust_moves(x_start,y_start):
    #     p.create_polygon(xy_figure(i[0], i[1]), fill='green', outline='black')

def logic_figure_horse( x_end, y_end, x_start, y_start): # логика поведения фигры "КОНЬ"
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
    for x in x_end:
        for y in y_end:
            if logic_figure_horse(x, y,x_start, y_start) == True:
                moves.append([x, y])
            y+=1
        x+=1
    return moves




def draw_board_cell(): #рисует клетки на доске
    i=0
    for x in range(8):
        for y in range(8):
            if i%2==0:
                p.create_rectangle(x*50+40, y*50+40, x*50+90, y*50+90, fill='#80461B')
            else:
                p.create_rectangle(x * 50+40, y * 50+40, x * 50 + 90, y * 50 + 90, fill='#FFDB8B')
            i+=1
        i-=1

def draw_cell_name(): # подписывает клетки
    name_x='ABCDEFGH'
    x, y = 65, 450
    for n in name_x:
        p.create_text(x,y, text=n)
        x+=50

    name_y='12345678'
    x, y = 25, 415
    for n in name_y:
        p.create_text(x, y, text=n)
        y -= 50

def init_ui(): # выводит окно приложения
    global window, p
    window = tkinter.Tk()
    window.geometry('640x480+300+100')
    window.minsize(640, 480)
    window.title('Chess')
    p = tkinter.Canvas()
    p.pack(fill=tkinter.BOTH, expand=True)
    p.create_rectangle(10, 10, 470, 470, fill='#FFDB8B')

def settings(): # Параметры приложения
    global x_start, y_start, window_geometry, window_fill, type_figure, callor_figure
    flag_x = False
    x = 'ABCDEFGH'
    while flag_x == False:
        x_start = str(input('от A до H: '))
        x_start = x_start.upper()
        if x_start in x:
            flag_x = True
            x_start = x.find(x_start) + 1

    flag_y = False
    y = '87654321'
    while flag_y == False:
        y_start = input('от 1 до 8: ')
        if y_start in y:
            y_start = y.find(y_start) + 1
            if 0 < y_start < 9:
                flag_y = True

    f = ('1', 'horse', 'конь')
    flag_f = False
    while flag_f == False:
        type_figure = str(input('Фигура: '))
        type_figure =type_figure.lower()
        if type_figure in f:
            type_figure = int(1)
            flag_f = True

    c_white = ( '1', 'white', 'белый', 'белая')
    c_black = ( '2', 'black', 'черный', 'черная')
    flag_c = False
    while flag_c == False:
        callor_figure = str(input('Цвет: '))
        callor_figure = callor_figure.lower()
        if callor_figure in c_white:
            callor_figure = 'white'
            flag_c = True
        if callor_figure in c_black:
            callor_figure = 'black'
            flag_c = True

def draw_move_figure (x_start, y_start, x_end, y_end, type_figure, callor_figure):  # рисует движение фигуры из А в Б
    draw_figure ( x=x_start, y=y_start, type_figure = type_figure, callor_figure = callor_figure)
    way = way_figure(x_start, y_start, type_figure, x_end, y_end)
    for m in way:
        draw_figure(x = m[0], y = m[1], type_figure = type_figure, callor_figure = callor_figure)



x_start = y_start = window_geometry = window_fill = type_figure = callor_figure = window = p = None

x_start =1
y_start=1
x_end=8
y_end=8
type_figure = 1
callor_figure = 'white'

# settings()
init_ui()
draw_board_cell()
draw_cell_name()
# draw_figure(x_start,y_start, type_figure, callor_figure)
# bust_moves()
# print(way_figure( x_start, y_start, type_figure, x_end, y_end))
draw_move_figure (x_start, y_start, x_end, y_end, type_figure, callor_figure)


window.mainloop()