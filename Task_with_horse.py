def bust_moves(cells): #перебор ходов для фигруры
    xy_start = cells
    xy_end = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)) # список возможных ходов
    moves=[]  # Список возможных ходов после проверки
    for xy in xy_end:
        new_x = xy_start[0] + xy[0]
        new_y = xy_start[1] + xy[1]
        if new_x > 0 and new_x < 9:
            if new_y > 0 and new_y < 9:
                moves.append((new_x,new_y))
    return moves

def way_figure( x_start, y_start, type_figure = 1): # Пытается решить задачу коня

    short_way = [[(x_start, y_start)]]
    flag_found_way = False
    bad_moves = dict () # Словарь плохихи ходов. {ход, (X,Y):  ходы куда ходить неи смысла}
    max_move = 0 #для отладки, пишет достигутый ход

    def check_moves (cells): # передаются предыдущие ходы, возваращаются возможные из них + словарь плохих ходов.
        cell = cells.copy() # Список предыдущих ходов.
        moves = []  #  Ходы куда в теории можно пойти перед проверкой.
        flag_return = True  # Флаг если не один ход не прошел проверку, то надо вернуться.
        moves_exit = []  # Варианты ходов на выход.
        while flag_return:
            moves = bust_moves(cell[-1]) #получить новые ходы
            flag_return = False # Если все ОК, то идем дальшей.
            for move in moves:  # проветка на повторение.
                move_list, key_move = [], []
                move_list.clear()
                move_list = cell.copy()
                key_move.extend(cell)
                key_move.append(move)
                key_move = tuple(key_move)
                if move not in cell and key_move not in bad_moves:
                    move_list.append(move)
                    moves_exit.append(move_list)
            if len(moves_exit) == 0: # Проверка, остались ли ходы.
                flag_return = True   # Тогда поднимаем флаг снова.
                key_cell = tuple(cell) # Делаем ключь для bad_moves.update   .
                bad_moves.add(key_cell)# Добовляем плохой ход в множество плохих ходов.
                cell.pop()   # Возвращаемся на один ход назад.
                # print(len(cell))

        return moves_exit, bad_moves

    while not flag_found_way:
        new_list_moves = []  # Список путей, из которого ввыбирается следующий ход, по правилу Варнсдорфа.
        for cells in short_way:
            moves_exit_get, bad_moves_get = check_moves(cells) # Получаем возможные ходы и словарь плохих.
            bad_moves.update(bad_moves_get) # Обновляем словарь плохих ходов.
            new_list_moves.extend(moves_exit_get)  # Список возможных путей заносим в new_list_moves для проверки мин.
        len_len = len(short_way[-1]) #Для отладки
        short_way.clear()
        if 63 > len_len: #Для отладки

            min_from_new_list_moves = min(new_list_moves)
        else:
            min_from_new_list_moves   = new_list_moves[0]   # Для отладки
        short_way.append(min_from_new_list_moves)
        if max_move < len(short_way[-1]):   #Для отладки
            max_move = len(short_way[-1])
            print(max_move)
        if len(short_way[-1]) > 63:     # Проверка на количество ходов
            flag_found_way = True
            print(short_way)
            break

    short_way = short_way[0] # По другому возвращает список списка туплов. так дальше не удобно
    return short_way



