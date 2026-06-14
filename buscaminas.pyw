import tkinter as tk
import random
import time


class Buscaminas:
    G = "#66BB6A"
    GD = "#43A047"
    W = "#F5F5F5"
    WD = "#E0E0E0"
    CBG = "#BDBDBD"
    DKG = "#0D200D"
    FLASH = "#A5D6A7"

    NUMS = ["", "#1565C0", "#2E7D32", "#C62828", "#6A1B9A",
            "#E65100", "#00695C", "#37474F", "#546E7A"]

    MCOL = ["#E53935", "#1E88E5", "#43A047", "#FB8C00",
            "#8E24AA", "#00ACC1", "#F4511E", "#3949AB",
            "#FDD835", "#6D4C41", "#00897B", "#5C6BC0"]

    def __init__(self, root):
        self.root = root
        self.root.title("Buscaminas")
        self.root.resizable(False, False)
        self.root.config(bg=self.DKG)

        self.diffs = {
            "50/50":  {"c": 2,  "r": 1,  "m": 1},
            "Facil":   {"c": 7,  "r": 7,  "m": 8},
            "Medio":   {"c": 14, "r": 14, "m": 30},
            "Dificil": {"c": 17, "r": 17, "m": 50},
            "Imposible": {"c": 1000, "r": 100, "m": 15000},
            "WTH":     {"c": 3,  "r": 3,  "m": 0},
        }
        self.cur = "Facil"
        self.S = 36
        self.gap = 1
        self.over = False
        self.first = True
        self.t0 = 0
        self.ticking = False
        self._animating = False
        self._game_id = 0
        self._after_id = None
        self._imp_clicks = 0

        self._ui()
        self.reset()

    def _ui(self):
        bar = tk.Frame(self.root, bg=self.DKG, padx=8, pady=4)
        bar.pack(fill=tk.X)

        left = tk.Frame(bar, bg=self.DKG)
        left.pack(side=tk.LEFT)

        tk.Label(left, text="Dificultad:", bg=self.DKG,
                 font=("Segoe UI", 9), fg="#E0E0E0").pack(side=tk.LEFT)
        self.dv = tk.StringVar(value=self.cur)
        dd = tk.OptionMenu(left, self.dv, *self.diffs, command=self._chg)
        dd.config(font=("Segoe UI", 9), bd=1, relief=tk.FLAT, bg="white")
        dd.pack(side=tk.LEFT, padx=4)

        tk.Button(left, text="Nuevo", command=self.reset,
                  font=("Segoe UI", 9), bd=1, relief=tk.FLAT,
                  overrelief=tk.RAISED, bg="white", cursor="hand2"
                  ).pack(side=tk.LEFT, padx=2)

        self.hbtn = tk.Button(left, text="Ayuda", command=self.help,
                              font=("Segoe UI", 9, "bold"), bd=1,
                              relief=tk.FLAT, overrelief=tk.RAISED,
                              bg="#FFC107", fg="#5D4037", cursor="hand2",
                              activebackground="#FFB300")
        self.hbtn.pack(side=tk.LEFT, padx=2)

        self.psst = tk.Button(left, text="psst", command=self._psst,
                              font=("Segoe UI", 8), bd=1, relief=tk.FLAT,
                              bg="#1E3A1E", fg="#66BB6A", cursor="hand2",
                              activebackground="#2E5C2E", activeforeground="#A5D6A7")
        self.psst.pack(side=tk.LEFT, padx=2)

        tk.Frame(bar, width=1, bg="#2E5C2E", height=24).pack(
            side=tk.LEFT, padx=8)

        self.mlbl = tk.Label(bar, text="0",
                             font=("Courier New", 14, "bold"),
                             fg="#EF5350", bg=self.DKG)
        self.mlbl.pack(side=tk.LEFT)

        tk.Label(bar, text="minas", font=("Segoe UI", 8),
                 fg="#81C784", bg=self.DKG).pack(side=tk.LEFT, padx=(2, 0))

        self.cara = tk.Label(bar, text=":-)", font=("Segoe UI", 18),
                             bg=self.DKG, cursor="hand2", fg="#E0E0E0")
        self.cara.pack(side=tk.LEFT, expand=True)
        self.cara.bind("<Button-1>", lambda e: self.reset())

        tk.Label(bar, text="reloj", font=("Segoe UI", 8),
                 fg="#81C784", bg=self.DKG).pack(side=tk.RIGHT, padx=(0, 2))
        self.tlbl = tk.Label(bar, text="0",
                             font=("Courier New", 14, "bold"),
                             fg="#E0E0E0", bg=self.DKG)
        self.tlbl.pack(side=tk.RIGHT)

        cf = tk.Frame(self.root, bg=self.DKG, bd=2, relief=tk.SUNKEN)
        cf.pack(padx=8, pady=4)

        self.cv = tk.Canvas(cf, highlightthickness=0, bg=self.CBG)
        self.cv.pack()

        self.cv.bind("<Button-1>", self._lc)
        self.cv.bind("<Button-3>", self._rc)

        self.hframe = tk.Frame(self.root, bg=self.DKG, height=28)
        self.hframe.pack(fill=tk.X, padx=8, pady=(0, 4))
        self.hframe.pack_propagate(False)

        self.hlbl = tk.Label(self.hframe, text=" ", fg="#81C784",
                             font=("Segoe UI", 9), wraplength=700,
                             bg=self.DKG, anchor=tk.W)
        self.hlbl.pack(fill=tk.BOTH)

    def _chg(self, d):
        self.cur = d
        self.reset()

    def _dark(self, c, amt=0.3):
        r = max(0, int(int(c[1:3], 16) * (1 - amt)))
        g = max(0, int(int(c[3:5], 16) * (1 - amt)))
        b = max(0, int(int(c[5:7], 16) * (1 - amt)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def reset(self):
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self._animating = False
        self._game_id += 1
        self.over = False
        self.first = True
        self.ticking = False
        self.tlbl.config(text="0")
        self.cara.config(text=":-)")
        self.hlbl.config(text=" ")
        if self.cur == "Imposible":
            self.psst.pack(side=tk.LEFT, padx=2)
        else:
            self.psst.pack_forget()
        self._imp_clicks = 0

        sz = {"50/50": 80, "Facil": 38, "Medio": 30, "Dificil": 26, "Imposible": 6, "WTH": 100}
        self.S = sz[self.cur]

        d = self.diffs[self.cur]
        self.C, self.R, self.M = d["c"], d["r"], d["m"]
        self.mlbl.config(text=str(self.M))

        self.cv.delete("all")
        step = self.S + self.gap
        w = self.gap + self.C * step
        h = self.gap + self.R * step
        self.cv.config(width=w, height=h)

        self.brd = [[0] * self.C for _ in range(self.R)]
        self.mns = [[False] * self.C for _ in range(self.R)]
        self.rev = [[False] * self.C for _ in range(self.R)]
        self.flg = [[False] * self.C for _ in range(self.R)]
        self.rects = [[None] * self.C for _ in range(self.R)]
        self.ovly = [[None] * self.C for _ in range(self.R)]
        self.fcnt = 0

        for r in range(self.R):
            for c in range(self.C):
                x1 = self.gap + c * step
                y1 = self.gap + r * step
                x2 = x1 + self.S
                y2 = y1 + self.S
                self.rects[r][c] = self.cv.create_rectangle(
                    x1, y1, x2, y2, fill=self.G, outline=self.GD, width=1)

        if self.cur == "WTH":
            self.ttt_board = [[""] * 3 for _ in range(3)]
            self.ttt_turn = "X"
            self.ttt_game_over = False
            self.mlbl.config(text="Turno: X")
            self.hlbl.config(text="Tres en raya! Haz clic para poner X.")

    def _place(self, sr, sc):
        avoid = {(sr, sc)}
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = sr + dr, sc + dc
                if 0 <= nr < self.R and 0 <= nc < self.C:
                    avoid.add((nr, nc))
        pos = [(r, c) for r in range(self.R) for c in range(self.C)
               if (r, c) not in avoid]
        if not pos:
            pos = [(r, c) for r in range(self.R) for c in range(self.C)]
        random.shuffle(pos)
        for r, c in pos[:self.M]:
            self.mns[r][c] = True
        for r in range(self.R):
            for c in range(self.C):
                if self.mns[r][c]:
                    self.brd[r][c] = -1
                else:
                    cnt = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.R and 0 <= nc < self.C and self.mns[nr][nc]:
                                cnt += 1
                    self.brd[r][c] = cnt

    def _gc(self, r, c):
        step = self.S + self.gap
        return self.gap + c * step, self.gap + r * step

    def _draw_flag(self, cx, cy):
        sz = self.S
        items = []
        px = cx - sz * 0.12
        py1 = cy - sz * 0.35
        py2 = cy + sz * 0.35
        items.append(self.cv.create_line(
            px, py2, px, py1, fill="#666",
            width=max(1.5, sz / 14)))
        items.append(self.cv.create_oval(
            px - 1.5, py2 - 1.5, px + 1.5, py2 + 1.5,
            fill="#666", outline=""))
        fs = sz * 0.32
        items.append(self.cv.create_polygon(
            px, py1,
            px + fs, py1 + fs * 0.55,
            px, py1 + fs,
            fill="#D32F2F", outline="#B71C1C", width=1))
        return items

    def _reveal_mine_cell(self, r, c):
        for item in self.ovly[r][c] or []:
            self.cv.delete(item)
        x, y = self._gc(r, c)
        cx = x + self.S // 2
        cy = y + self.S // 2
        if self.mns[r][c]:
            if self.flg[r][c]:
                self.cv.itemconfig(self.rects[r][c],
                                   fill="#D32F2F", outline="#B71C1C")
                self.ovly[r][c] = [self.cv.create_text(
                    cx, cy, text="*", fill="white",
                    font=("Segoe UI", self.S // 2 + 1, "bold"))]
            else:
                col = random.choice(self.MCOL)
                dot = self._dark(col, 0.5)
                self.cv.itemconfig(self.rects[r][c],
                                   fill=col, outline=self._dark(col, 0.2))
                rd = max(2, self.S // 5)
                self.ovly[r][c] = [self.cv.create_oval(
                    cx - rd, cy - rd, cx + rd, cy + rd,
                    fill=dot, outline=dot)]
        elif self.flg[r][c] and not self.mns[r][c]:
            self.cv.itemconfig(self.rects[r][c],
                               fill=self.W, outline="#D32F2F")
            self.ovly[r][c] = [self.cv.create_text(
                cx, cy, text="X", fill="#D32F2F",
                font=("Segoe UI", self.S // 2 + 1, "bold"))]

    def _lc(self, evt):
        if self.over or self._animating:
            return
        step = self.S + self.gap
        c = evt.x // step
        r = evt.y // step
        if not (0 <= r < self.R and 0 <= c < self.C):
            return

        if self.cur == "WTH":
            if self.ttt_game_over:
                return
            if self.ttt_board[r][c] != "":
                return
            if not self.ticking:
                self.t0 = time.time()
                self.ticking = True
                self._tick()
            self.ttt_board[r][c] = "X"
            self._ttt_draw_move(r, c, "X")
            winner = self._ttt_check_win()
            self.mlbl.config(text="Pensando...")
            self.cara.config(text="O_o")
            if winner == "X":
                self.over = True
                self.ttt_game_over = True
                self.ticking = False
                self.cara.config(text="B-)")
                self.hlbl.config(text="Ganaste!")
                self.mlbl.config(text="Gana X")
                return
            elif winner == "draw":
                self.over = True
                self.ttt_game_over = True
                self.ticking = False
                self.cara.config(text="-_-")
                self.hlbl.config(text="Empate!")
                self.mlbl.config(text="Empate")
                return
            self.ttt_turn = "O"
            gid = self._game_id
            self._animating = True
            self.root.after(300, lambda: self._ttt_ai_go(gid))
            return

        if self.flg[r][c] or self.rev[r][c]:
            return
        if not self.ticking:
            self.t0 = time.time()
            self.ticking = True
            self._tick()
        if self.first:
            self._place(r, c)
            self.first = False
        if self.mns[r][c]:
            self.over = True
            self.ticking = False
            self.cara.config(text="X_X")
            self._anim_loss(r, c)
            return
        if self.cur == "Imposible":
            self._imp_clicks += 1
            total = self.R * self.C
            side = int((total * 0.03) ** 0.5)
            radius = max(1, int(side // 2 * (1.05 ** (self._imp_clicks - 1))))
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.R and 0 <= nc < self.C:
                        if not self.mns[nr][nc] and not self.rev[nr][nc] and not self.flg[nr][nc]:
                            self._rev(nr, nc)
            self._win()
            return
        gid = self._game_id
        self._animating = True
        self.cv.itemconfig(self.rects[r][c], fill=self.FLASH, outline="#66BB6A")
        self.root.after(50, lambda: self._end_reveal(r, c, gid))

    def _end_reveal(self, r, c, gid):
        self._animating = False
        if gid != self._game_id or self.over:
            return
        self._rev(r, c)
        self._win()

    def _anim_loss(self, fr, fc):
        self._reveal_mine_cell(fr, fc)
        self._reveal_queue = []
        for r in range(self.R):
            for c in range(self.C):
                if r == fr and c == fc:
                    continue
                if self.mns[r][c] or (self.flg[r][c] and not self.mns[r][c]):
                    self._reveal_queue.append((r, c))
        random.shuffle(self._reveal_queue)
        self._reveal_idx = 0
        self._reveal_delay = 150
        self._anim_step()

    def _anim_step(self):
        if not self.over:
            return
        if self._reveal_idx >= len(self._reveal_queue):
            return
        r, c = self._reveal_queue[self._reveal_idx]
        self._reveal_idx += 1
        self._reveal_mine_cell(r, c)
        self._reveal_delay = max(10, int(self._reveal_delay * 0.88))
        self._after_id = self.root.after(self._reveal_delay, self._anim_step)

    def _rc(self, evt):
        if self.over or self._animating:
            return
        step = self.S + self.gap
        c = evt.x // step
        r = evt.y // step
        if not (0 <= r < self.R and 0 <= c < self.C):
            return
        if self.cur == "WTH":
            return
        if self.rev[r][c]:
            return
        if self.flg[r][c]:
            self.flg[r][c] = False
            self.fcnt -= 1
            self.mlbl.config(text=str(self.M - self.fcnt))
            for item in self.ovly[r][c] or []:
                self.cv.delete(item)
            self.ovly[r][c] = None
            self.cv.itemconfig(self.rects[r][c], fill=self.G, outline=self.GD)
        else:
            self.flg[r][c] = True
            self.fcnt += 1
            self.mlbl.config(text=str(self.M - self.fcnt))
            gid = self._game_id
            self._animating = True
            self.cv.itemconfig(self.rects[r][c], fill=self.G, outline="#D32F2F")
            x, y = self._gc(r, c)
            cx = x + self.S // 2
            cy = y + self.S // 2
            px = cx - self.S * 0.12
            bot = cy + self.S * 0.35
            mid = cy
            items = [self.cv.create_line(
                px, bot, px, mid, fill="#666",
                width=max(1.5, self.S / 14))]
            self.ovly[r][c] = items
            self.root.after(50, lambda: self._end_flag(r, c, gid))

    def _end_flag(self, r, c, gid):
        self._animating = False
        if gid != self._game_id or self.over:
            return
        for item in self.ovly[r][c] or []:
            self.cv.delete(item)
        x, y = self._gc(r, c)
        cx = x + self.S // 2
        cy = y + self.S // 2
        self.ovly[r][c] = self._draw_flag(cx, cy)

    def _rev(self, r, c):
        if self.rev[r][c] or self.flg[r][c]:
            return
        self.rev[r][c] = True
        x, y = self._gc(r, c)
        cx = x + self.S // 2
        cy = y + self.S // 2
        for item in self.ovly[r][c] or []:
            self.cv.delete(item)
        self.ovly[r][c] = None
        self.cv.itemconfig(self.rects[r][c], fill=self.W, outline=self.WD)
        if self.brd[r][c] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.R and 0 <= nc < self.C:
                        self._rev(nr, nc)
        else:
            n = self.brd[r][c]
            sz = self.S // 2 + 2
            self.ovly[r][c] = [self.cv.create_text(
                cx, cy, text=str(n), fill=self.NUMS[n],
                font=("Segoe UI", sz, "bold"))]

    WIN_MSGS = [
        "Sobreviviste.",
        "Tocaste pasto hoy? No.",
        "El gobierno teme tu poder.",
        "Buscaminero certificado.",
    ]

    def _win(self):
        if self.cur == "WTH":
            return
        cnt = sum(1 for r in range(self.R) for c in range(self.C)
                  if self.rev[r][c])
        if cnt == self.R * self.C - self.M:
            self.over = True
            self.ticking = False
            self.cara.config(text="B-)")
            if self.cur == "Imposible":
                self.cv.create_text(
                    self.cv.winfo_reqwidth() // 2,
                    self.cv.winfo_reqheight() // 2,
                    text=random.choice(self.WIN_MSGS),
                    fill="#FFD700", font=("Segoe UI", 24, "bold"))
            for r in range(self.R):
                for c in range(self.C):
                    if self.mns[r][c] and not self.flg[r][c]:
                        self.flg[r][c] = True
                        x, y = self._gc(r, c)
                        cx = x + self.S // 2
                        cy = y + self.S // 2
                        self.cv.itemconfig(self.rects[r][c],
                                           fill=self.G, outline="#D32F2F")
                        self.ovly[r][c] = self._draw_flag(cx, cy)

    def _tick(self):
        if not self.ticking:
            return
        t = int(time.time() - self.t0)
        self.tlbl.config(text=str(t))
        self.root.after(1000, self._tick)

    def _ttt_draw_move(self, r, c, player):
        x, y = self._gc(r, c)
        cx = x + self.S // 2
        cy = y + self.S // 2
        for item in self.ovly[r][c] or []:
            self.cv.delete(item)
        if player == "O":
            self.ovly[r][c] = self._draw_flag(cx, cy)
            self.cv.itemconfig(self.rects[r][c], fill=self.G, outline="#D32F2F")
        else:
            num = r * 3 + c + 1
            sz = self.S // 2
            self.ovly[r][c] = [self.cv.create_text(
                cx, cy, text=str(num), fill="#2196F3",
                font=("Segoe UI", sz, "bold"))]
            self.cv.itemconfig(self.rects[r][c], fill=self.W, outline=self.WD)

    def _ttt_check_win(self):
        b = self.ttt_board
        for r in range(3):
            if b[r][0] == b[r][1] == b[r][2] != "":
                return b[r][0]
        for c in range(3):
            if b[0][c] == b[1][c] == b[2][c] != "":
                return b[0][c]
        if b[0][0] == b[1][1] == b[2][2] != "":
            return b[0][0]
        if b[0][2] == b[1][1] == b[2][0] != "":
            return b[0][2]
        if all(b[r][c] != "" for r in range(3) for c in range(3)):
            return "draw"
        return None

    def _ttt_get_ai_move(self):
        b = self.ttt_board
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    b[r][c] = "O"
                    if self._ttt_check_win() == "O":
                        b[r][c] = ""
                        return r, c
                    b[r][c] = ""
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    b[r][c] = "X"
                    if self._ttt_check_win() == "X":
                        b[r][c] = ""
                        return r, c
                    b[r][c] = ""
        if b[1][1] == "":
            return 1, 1
        for r, c in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            if b[r][c] == "":
                return r, c
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    return r, c
        return 0, 0

    def _ttt_ai_go(self, gid):
        self._animating = False
        if gid != self._game_id or self.over:
            return
        r, c = self._ttt_get_ai_move()
        self.ttt_board[r][c] = "O"
        self._ttt_draw_move(r, c, "O")
        winner = self._ttt_check_win()
        if winner == "O":
            self.over = True
            self.ttt_game_over = True
            self.ticking = False
            self.cara.config(text="X_X")
            self.hlbl.config(text="Perdiste!")
            self.mlbl.config(text="Gana O")
            return
        elif winner == "draw":
            self.over = True
            self.ttt_game_over = True
            self.ticking = False
            self.cara.config(text="-_-")
            self.hlbl.config(text="Empate!")
            self.mlbl.config(text="Empate")
            return
        self.ttt_turn = "X"
        self.mlbl.config(text="Turno: X")
        self.cara.config(text=":-)")

    def _psst(self):
        if self.cur == "WTH":
            return
        if self.cur != "Imposible" or self.over or self._animating:
            return
        if self.first:
            self._place(0, 0)
            self.first = False
            if not self.ticking:
                self.t0 = time.time()
                self.ticking = True
                self._tick()
        self._psst_queue = []
        for r in range(self.R):
            for c in range(self.C):
                if not self.rev[r][c] and not self.flg[r][c]:
                    self._psst_queue.append((r, c))
        random.shuffle(self._psst_queue)
        self._psst_idx = 0
        self._psst_batch = 1
        self._psst_delay = 20
        self._animating = True
        self._psst_step()

    def _psst_step(self):
        if self.over or not self._animating:
            self._animating = False
            return
        if self._psst_idx >= len(self._psst_queue):
            self._animating = False
            self.mlbl.config(text=str(self.M - self.fcnt))
            self._win()
            return
        batch = self._psst_batch
        for _ in range(batch):
            if self._psst_idx >= len(self._psst_queue):
                break
            r, c = self._psst_queue[self._psst_idx]
            self._psst_idx += 1
            if self.mns[r][c]:
                self.flg[r][c] = True
                self.fcnt += 1
                x, y = self._gc(r, c)
                cx = x + self.S // 2
                cy = y + self.S // 2
                self.cv.itemconfig(self.rects[r][c], fill=self.G, outline="#D32F2F")
                self.ovly[r][c] = self._draw_flag(cx, cy)
            else:
                self.rev[r][c] = True
                x, y = self._gc(r, c)
                cx = x + self.S // 2
                cy = y + self.S // 2
                for item in self.ovly[r][c] or []:
                    self.cv.delete(item)
                self.ovly[r][c] = None
                self.cv.itemconfig(self.rects[r][c], fill=self.W, outline=self.WD)
                if self.brd[r][c] > 0:
                    sz = self.S // 2 + 2
                    self.ovly[r][c] = [self.cv.create_text(
                        cx, cy, text=str(self.brd[r][c]), fill=self.NUMS[self.brd[r][c]],
                        font=("Segoe UI", sz, "bold"))]
        self.mlbl.config(text=str(self.M - self.fcnt))
        self._psst_batch = min(self._psst_batch * 2, 5000)
        self._psst_delay = max(1, int(self._psst_delay * 0.9))
        self._after_id = self.root.after(self._psst_delay, self._psst_step)

    def help(self):
        if self.cur == "WTH":
            if self.over:
                self.hlbl.config(text="Juego terminado! Presiona 'Nuevo' para reiniciar.")
                return
            if self.ttt_turn == "O":
                self.hlbl.config(text="Espera tu turno...")
                return
            b = self.ttt_board
            best = None
            for r in range(3):
                for c in range(3):
                    if b[r][c] == "":
                        b[r][c] = "X"
                        if self._ttt_check_win() == "X":
                            b[r][c] = ""
                            best = (r, c)
                        b[r][c] = ""
            if not best:
                for r in range(3):
                    for c in range(3):
                        if b[r][c] == "":
                            b[r][c] = "O"
                            if self._ttt_check_win() == "O":
                                b[r][c] = ""
                                best = (r, c)
                            b[r][c] = ""
            if not best and b[1][1] == "":
                best = (1, 1)
            if not best:
                for r, c in [(0,0), (0,2), (2,0), (2,2)]:
                    if b[r][c] == "":
                        best = (r, c)
                        break
            if not best:
                for r in range(3):
                    for c in range(3):
                        if b[r][c] == "":
                            best = (r, c)
                            break
                    if best: break
            for r in range(3):
                for c in range(3):
                    if b[r][c] == "":
                        self.cv.itemconfig(self.rects[r][c], fill=self.G, outline=self.GD)
                    elif b[r][c] == "X":
                        self.cv.itemconfig(self.rects[r][c], fill=self.W, outline=self.WD)
                    else:
                        self.cv.itemconfig(self.rects[r][c], fill=self.G, outline="#D32F2F")
            if best:
                self.cv.itemconfig(self.rects[best[0]][best[1]], fill="#A5D6A7", outline="#66BB6A")
                self.hlbl.config(text=f"Sugerencia: juega en ({best[0]+1},{best[1]+1})")
            else:
                self.hlbl.config(text="Tablero lleno!")
            return
        if self.cur == "50/50":
            self.hlbl.config(text="No hay solucion logica, es 50/50.")
            return
        if self.over or self.first:
            self.hlbl.config(
                text="Haz clic en cualquier casilla para empezar.")
            return

        for r in range(self.R):
            for c in range(self.C):
                if self.rev[r][c]:
                    self.cv.itemconfig(self.rects[r][c],
                                       fill=self.W, outline=self.WD)
                elif self.flg[r][c]:
                    self.cv.itemconfig(self.rects[r][c],
                                       fill=self.G, outline="#D32F2F")
                else:
                    self.cv.itemconfig(self.rects[r][c],
                                       fill=self.G, outline=self.GD)

        suggestions = []

        for r in range(self.R):
            for c in range(self.C):
                if not self.rev[r][c] or self.brd[r][c] <= 0:
                    continue
                n = self.brd[r][c]
                bcnt = 0
                hidden = []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.R and 0 <= nc < self.C:
                            if self.flg[nr][nc]:
                                bcnt += 1
                            if not self.rev[nr][nc] and not self.flg[nr][nc]:
                                hidden.append((nr, nc))
                if bcnt == n and hidden:
                    for h in hidden[:3]:
                        suggestions.append(("click", h))
                        self.cv.itemconfig(self.rects[h[0]][h[1]],
                                           fill="#A5D6A7", outline="#66BB6A")
                if bcnt < n and len(hidden) == n - bcnt and hidden:
                    for h in hidden[:3]:
                        suggestions.append(("flag", h))
                        self.cv.itemconfig(self.rects[h[0]][h[1]],
                                           fill="#EF9A9A", outline="#E53935")

        if not suggestions and self.fcnt == self.M:
            for r in range(self.R):
                for c in range(self.C):
                    if not self.rev[r][c] and not self.flg[r][c]:
                        suggestions.append(("click", (r, c)))
                        self.cv.itemconfig(self.rects[r][c],
                                           fill="#A5D6A7", outline="#66BB6A")

        if not suggestions:
            restantes = sum(1 for r in range(self.R) for c in range(self.C)
                            if not self.rev[r][c] and not self.flg[r][c])
            minas_rest = self.M - self.fcnt
            if restantes == minas_rest and restantes > 0:
                for r in range(self.R):
                    for c in range(self.C):
                        if not self.rev[r][c] and not self.flg[r][c]:
                            suggestions.append(("flag", (r, c)))
                            self.cv.itemconfig(self.rects[r][c],
                                               fill="#EF9A9A", outline="#E53935")

        if not suggestions:
            restantes = sum(1 for r in range(self.R) for c in range(self.C)
                            if not self.rev[r][c] and not self.flg[r][c])
            minas_rest = self.M - self.fcnt
            densidad = minas_rest / restantes if restantes > 0 else 0

            best = []
            for r in range(self.R):
                for c in range(self.C):
                    if self.rev[r][c] or self.flg[r][c]:
                        continue
                    probs = []
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            nr, nc = r + dr, c + dc
                            if not (0 <= nr < self.R and 0 <= nc < self.C):
                                continue
                            if not self.rev[nr][nc] or self.brd[nr][nc] <= 0:
                                continue
                            n = self.brd[nr][nc]
                            bcnt = 0
                            ocultos = 0
                            for dr2 in (-1, 0, 1):
                                for dc2 in (-1, 0, 1):
                                    nr2, nc2 = nr + dr2, nc + dc2
                                    if 0 <= nr2 < self.R and 0 <= nc2 < self.C:
                                        if self.flg[nr2][nc2]:
                                            bcnt += 1
                                        if not self.rev[nr2][nc2] and not self.flg[nr2][nc2]:
                                            ocultos += 1
                            if ocultos > 0:
                                probs.append((n - bcnt) / ocultos)
                    prob = sum(probs) / len(probs) if probs else densidad
                    best.append(((r, c), prob))

            best.sort(key=lambda x: x[1])
            for (r, c), p in best[:3]:
                suggestions.append(("guess", (r, c)))
                self.cv.itemconfig(self.rects[r][c],
                                   fill="#FFF59D", outline="#F9A825")

        txts = []
        for t, pos in suggestions[:8]:
            if t == "click":
                txts.append(f"Click ({pos[0]+1},{pos[1]+1})")
            elif t == "flag":
                txts.append(f"Bandera ({pos[0]+1},{pos[1]+1})")
            else:
                txts.append(f"? Click ({pos[0]+1},{pos[1]+1})")
        self.hlbl.config(text="Sugerencias: " + " | ".join(txts))


if __name__ == "__main__":
    root = tk.Tk()
    Buscaminas(root)
    root.mainloop()
