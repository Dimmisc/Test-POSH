import requests
from pprint import pprint

url = "https://olimp.miet.ru/ppo_it/api"

def get_data():
    res = requests.get(url)
    if res and "message" in res.json() and "data" in res.json()["message"]:
        return res.json()["message"]["data"]
    return None

def insert(base, chunk, x, y):
    for i in range(len(chunk)):
        for j in range(len(chunk[0])):
            base[x + i][y + j] = chunk[i][j]
    return base

map = [[[-1] for _ in range(256*2 - 64)] for _ in range(256*2-64)]
first_chunk = get_data()


class chunk:
    left = []
    right = []
    top = []
    down = []

    full_data = []  

    def _count_coef(self, spi):
        return [(sum(spi[i:i + 4]) / 4) ** 2 for i in range(0, len(spi), 4)]
    
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
        
    def check_right(self, other):
        return sum((self.rcoef[i] - other.lcoef[i]) ** 2 for i in range(len(self.rcoef)))
    
    def check_bottom(self, other):
        return sum((self.dcoef[i] - other.tcoef[i]) ** 2 for i in range(len(self.dcoef)))

    def check_top(self, other):
        return sum((self.tcoef[i] - other.dcoef[i]) ** 2 for i in range(len(self.tcoef)))
    
    def check_left(self, other):
        return sum((self.lcoef[i] - other.rcoef[i]) ** 2 for i in range(len(self.lcoef)))

    def check(self, other):
        if self.left == other.left and self.right == other.right and self.top == other.top and self.bottom == other.bottom:
            return True
        return False
    
    def print(self):
        print("left: ", sum(self.left) / 64, "right: ", sum(self.right) / 64, "top: ", sum(self.top) / 64, "down: ", sum(self.bottom) / 64)

    def __repr__(self):
        return "c "


chuncks = [chunk(first_chunk)]

while len(chuncks) != 16:
    new_chunck = chunk(get_data())
    if sum([1 for c in chuncks if c.check(new_chunck)]) == 0:
        chuncks.append(new_chunck)
        print(f"Chunck added: {len(chuncks)}")

map = [[-1 for i in range(7)] for i in range(7)]
map[3][3] = chuncks.pop()

def check(map, crd):
    chund: chunk = map[crd[0]][crd[1]]
    res = ""
    if (sum(chund.right) / 64 != 255) and crd[1] < 6 and map[crd[0]][crd[1] + 1] == -1:res += "r"
    if (sum(chund.left) / 64 != 255) and  crd[1] > 0 and map[crd[0]][crd[1] - 1] == -1:res += "l"
    if (sum(chund.bottom) / 64 != 255) and crd[0] < 6 and map[crd[0] + 1][crd[1]] == -1:res += "d"
    if (sum(chund.top) / 64 != 255) and  crd[0] > 0 and map[crd[0] - 1][crd[1]] == -1:res += "t"
        
    return res


staned_map = [[3, 3]]
pprint(map)
print()

while len(chuncks) != 0:
    for cds in staned_map:
        m_chunck = map[cds[0]][cds[1]]
        ch_m = check(map, cds)
        
        rcmin, lcmin, dcmin, tcmin = 1e9, 1e9, 1e9, 1e9
        # r_side_min
        irmn, ilmn, idmn, itmn = -1, -1, -1, -1
        # r_ind_min
        
        if ch_m == "":
            staned_map.remove(cds)
            continue
        
        if "r" in ch_m:
            for j in range(len(chuncks)):
                rnc = m_chunck.check_right(chuncks[j])
                if rcmin > rnc:
                    rcmin = rnc
                    irmn = j
        if "l" in ch_m:
            for j in range(len(chuncks)):
                lnc = m_chunck.check_left(chuncks[j])
                if lcmin > lnc:
                    lcmin = lnc
                    ilmn = j
        if "d" in ch_m:
            for j in range(len(chuncks)):
                dnc = m_chunck.check_bottom(chuncks[j])
                if dcmin > dnc:
                    dcmin = dnc
                    idmn = j
        if "t" in ch_m:  
            for j in range(len(chuncks)):
                tnc = m_chunck.check_top(chuncks[j])
                if tcmin > tnc:
                    tcmin = tnc
                    itmn = j  
                    
        mi = min([tcmin, dcmin, lcmin, rcmin])

        if mi == tcmin and itmn != -1:
            map[cds[0] - 1][cds[1]] = chuncks.pop(itmn)
            staned_map.append([cds[0] - 1, cds[1]])
            break
        elif mi == dcmin and idmn != -1:
            map[cds[0] + 1][cds[1]] = chuncks.pop(idmn)
            staned_map.append([cds[0] + 1, cds[1]])
            break
        elif mi == lcmin and ilmn != -1:
            map[cds[0]][cds[1] - 1] = chuncks.pop(ilmn)
            staned_map.append([cds[0], cds[1] - 1])
            break
        elif mi == rcmin and irmn != -1: 
            map[cds[0]][cds[1] + 1] = chuncks.pop(irmn)
            staned_map.append([cds[0], cds[1] + 1])
            break


final_map = [[[0]* 4] * 4]
x, y = 0, 0
flag = False
for i in range(7):
    if flag:
        break
    for j in range(7):
        if map[i][j] != -1:
            x, y = i, j
            flag = True
            break
        
for i in range(x, x + 4):
    for j in range(y, y + 4):i
        