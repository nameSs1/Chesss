def bust_moves(xy_start): #перебор ходов для фигруры
    xy_end = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)] # список возможных ходов
    moves=[]  # Список возможных ходов после проверки
    for xy in xy_end:
        new_x = xy_start[0] + xy[0]
        new_y = xy_start[1] + xy[1]
        if new_x > 0 and new_x < 9:
            if new_y > 0 and new_y < 9:
                moves.append((new_x,new_y))
    return moves

def way_figure( x_start, y_start, type_figure, x_finish = None, y_finish = None): #вычисляет путь фигуры от А к Б

    short_way = [[(x_start, y_start)]]
    flag_found_way = False
    bad_moves = {}  # Словарь плохихи ходов. Ключ -- предшествующие ходы, значение -- куда ходить после них не стоит.

    def check_moves ( cells): # передаются предыдущие ходы, возваращаются возможные из них + словарь плохих ходов.
        cells = cells # Список предыдущих ходов.
        moves = []  #  Ходы куда в теории можно пойти перед проверкой.
        flag_return = True  # Флаг если не один ход не прошел проверку, то надо вернуться.
        moves_exit = []  # Варианты ходов на выход.
        while flag_return == True:
            moves = bust_moves(cells[-1]) #получить новые ходы
            flag_return = False # Если все ОК, то идем дальшей.
            for move in moves:  # проветка на повторение.
                move_list = []
                move_list.clear()
                move_list = cell.copy()
                move_list.append(move)
                key_move = tuple(move_list)
                if move in cell:
                    continue
                elif key_move in bad_moves: # Проверка на плохой ход. tuple?. -2?.
                    continue
                else:
                    moves_exit.append(move_list)
            if len(moves_exit) == 0: # Проверка, остались ли ходы.
                flag_return = True   # Тогда поднимаем флаг снова.
                key_cells = tuple(cells[:-1]) # Делаем ключь для bad_moves.update   .
                bad_moves.update(key_cells = cells[-1]) # Добовляем плохой ход в словарь плохих ходов.
                cells = cells[:-1]   # Возвращаемся на один ход назад.
        return moves_exit, bad_moves

    while flag_found_way == False:
        new_list_moves = []  # Список путей, из которого ввыбирается следующий ход, по правилу Варнсдорфа.
        for cell in short_way:
            moves_exit_get, bad_moves_get = check_moves(cell) # Получаем возможные ходы и словарь плохих.
            bad_moves.update(bad_moves_get) # Обновляем словарь плохих ходов.
            new_list_moves.append(moves_exit_get)  # Список возможных путей заносим в new_list_moves для проверки мин.
        short_way.clear()
        min_from_new_list_moves = min(new_list_moves)
        short_way = min_from_new_list_moves
        if len(short_way[-1]) > 63:     # Проверка на количество ходов
            flag_found_way = True
            print(short_way)
            break

    return short_way

way_figure(1,5,1)

