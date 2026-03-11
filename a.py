import requests
from pprint import pprint

url = "https://olimp.miet.ru/ppo_it/api"

def get_data():
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if "message" in data and "data" in data["message"]:
            # Явно приводим все значения к int, как того требует ТЗ (0-255)
            return [[int(val) for val in row] for row in data["message"]["data"]]
    return None

def get_stations():
    res = requests.get(url + '/coords')
    if res.status_code == 200:
        data = res.json()
        if 'message' in data:
            return data['message'] 
    return None


class Chunk:
    left = []
    right = []
    top = []
    bottom = []
    full_data = []

    def __init__(self, data):
        self.top = data[0]
        self.bottom = data[-1]
        self.left = [row[0] for row in data]
        self.right = [row[-1] for row in data]
        self.full_data = data
        
        self.lcoef = self._count_coef(self.left)
        self.rcoef = self._count_coef(self.right)
        self.tcoef = self._count_coef(self.top)
        self.dcoef = self._count_coef(self.bottom)

    def _count_coef(self, spi):
        return [spi[i] ** 2 for i in range(len(spi))]
        
    def check_right(self, other):
        return sum((self.rcoef[i] - other.lcoef[i]) ** 2 for i in range(len(self.rcoef)))
    
    def check_bottom(self, other):
        return sum((self.dcoef[i] - other.tcoef[i]) ** 2 for i in range(len(self.dcoef)))

    def check_top(self, other):
        return sum((self.tcoef[i] - other.dcoef[i]) ** 2 for i in range(len(self.tcoef)))
    
    def check_left(self, other):
        return sum((self.lcoef[i] - other.rcoef[i]) ** 2 for i in range(len(self.lcoef)))

    def is_same(self, other):
        return self.full_data == other.full_data
    
    def __repr__(self):
        return "c "


# --- 1. Сбор 16 уникальных чанков ---
print("Собираем фрагменты карты (16 тайлов 64x64)...")
chunks = []
while len(chunks) < 16:
    data = get_data()
    if data:
        new_chunk = Chunk(data)
        if not any(c.is_same(new_chunk) for c in chunks):
            chunks.append(new_chunk)
            print(f"Собрано {len(chunks)}/16 тайлов")


# --- 2. Инициализация карты ---
chunk_map = [[-1 for _ in range(7)] for _ in range(7)]
chunk_map[3][3] = chunks.pop()
staned_map = [[3, 3]]

def get_open_sides(c_map, crd):
    res = ""
    r, c = crd
    chund : Chunk = c_map[r][c]
    if (sum(chund.right) / 64 != 255) and c < 6 and c_map[r][c + 1] == -1: res += "r"
    if (sum(chund.left) / 64 != 255) and c > 0 and c_map[r][c - 1] == -1: res += "l"
    if (sum(chund.bottom) / 64 != 255) and r < 6 and c_map[r + 1][c] == -1: res += "d"
    if (sum(chund.top) / 64 != 255) and r > 0 and c_map[r - 1][c] == -1: res += "t"
    return res


# --- 3. Сборка пазла ---
print("Собираем пазл...")
while chunks:
    placed = False
    for cds in list(staned_map):
        r, c = cds
        m_chunk = chunk_map[r][c]
        ch_m = get_open_sides(chunk_map, cds)
        
        if ch_m == "":
            staned_map.remove(cds)
            continue
        
        rcmin, lcmin, dcmin, tcmin = 1e9, 1e9, 1e9, 1e9
        irmn, ilmn, idmn, itmn = -1, -1, -1, -1
        
        if "r" in ch_m:
            for j, ch in enumerate(chunks):
                rnc = m_chunk.check_right(ch)
                if rnc < rcmin: rcmin, irmn = rnc, j
        if "l" in ch_m:
            for j, ch in enumerate(chunks):
                lnc = m_chunk.check_left(ch)
                if lnc < lcmin: lcmin, ilmn = lnc, j
        if "d" in ch_m:
            for j, ch in enumerate(chunks):
                dnc = m_chunk.check_bottom(ch)
                if dnc < dcmin: dcmin, idmn = dnc, j
        if "t" in ch_m:  
            for j, ch in enumerate(chunks):
                tnc = m_chunk.check_top(ch)
                if tnc < tcmin: tcmin, itmn = tnc, j  

        mi = min([tcmin, dcmin, lcmin, rcmin])
        
        if mi == tcmin and itmn != -1:
            chunk_map[r - 1][c] = chunks.pop(itmn)
            staned_map.append([r - 1, c])
            placed = True
        elif mi == dcmin and idmn != -1:
            chunk_map[r + 1][c] = chunks.pop(idmn)
            staned_map.append([r + 1, c])
            placed = True
        elif mi == lcmin and ilmn != -1:
            chunk_map[r][c - 1] = chunks.pop(ilmn)
            staned_map.append([r, c - 1])
            placed = True
        elif mi == rcmin and irmn != -1:
            chunk_map[r][c + 1] = chunks.pop(irmn)
            staned_map.append([r, c + 1])
            placed = True
            
        if placed:
            break

print("Карта собрана!")
pprint(chunk_map)


valid_cells = [(r, c) for r in range(7) for c in range(7) if isinstance(chunk_map[r][c], Chunk)]

if not valid_cells:
    print("Ошибка: карта не была собрана.")
else:
    min_r = min(x[0] for x in valid_cells)
    min_c = min(x[1] for x in valid_cells)
    
    # Склеиваем данные в единый 2D массив (256x256)
    full_image = []
    # Мы знаем, что карта 4x4 тайла
    for r in range(min_r, min_r + 4): 
        # Проверяем, что в текущей строке тайлы существуют
        for row_i in range(64):
            row_data = []
            for c in range(min_c, min_c + 4): 
                # Если вдруг какой-то тайл не найден (на случай ошибок), заполним нулями
                if isinstance(chunk_map[r][c], Chunk):
                    row_data.extend(chunk_map[r][c].full_data[row_i])
                else:
                    row_data.extend([0] * 64)
            full_image.append(row_data)

    print(f"Итоговый размер карты: {len(full_image)}x{len(full_image[0])} пикселей")

    # --- 5. Получение координат и извлечение данных ---
    stations_data = get_stations()

    if stations_data:
        # sender/listener возвращают [x, y], где x - столбец, y - строка
        # В API это скорее всего словарь с ключами 'sender' и 'listener'
        sender_x, sender_y = stations_data['sender']
        listener_x, listener_y = stations_data['listener']
        
        cuper_price, engel_price = stations_data['price']
        
        # Обращение к матрице: array[y][x]
        # Проверяем границы, чтобы не вылететь, если координаты вне 256x256
        if 0 <= sender_y < 256 and 0 <= sender_x < 256:
            sender_depth = full_image[sender_y][sender_x]
            print(f"Модуль 'Эл-12' (Sender) высота: {sender_depth} (X:{sender_x}, Y:{sender_y})")
            
        if 0 <= listener_y < 256 and 0 <= listener_x < 256:
            listener_depth = full_image[listener_y][listener_x]
            print(f"Модуль 'Фар-3' (Listener) высота: {listener_depth} (X:{listener_x}, Y:{listener_y})")
            
        print(f"Стоимость станций: Купер = {cuper_price}, Энгель = {engel_price}")
    else:
        print("Не удалось получить данные о станциях.")

import matplotlib.pyplot as plt

# --- 6. Визуализация карты (Добавьте это в конец вашего кода) ---
if 'full_image' in locals():
    # Преобразуем список списков в массив numpy для удобства matplotlib
    import numpy as np
    img_array = np.array(full_image)

    plt.figure(figsize=(8, 8))
    # 'terrain' — хорошая цветовая карта для рельефа
    plt.imshow(img_array, cmap='terrain', origin='upper')
    plt.colorbar(label='Высота (0-255)')
    
    # Отмечаем модули
    if 'stations_data' in locals():
        s_x, s_y = stations_data['sender']
        l_x, l_y = stations_data['listener']
        
        plt.scatter(s_x, s_y, color='red', marker='X', s=100, label='Sender (Эл-12)')
        plt.scatter(l_x, l_y, color='blue', marker='X', s=100, label='Listener (Фар-3)')
    
    plt.title("Марсианская поверхность")
    plt.legend()
    plt.show()
else:
    print("Ошибка: карта не собрана, нечего отображать.")