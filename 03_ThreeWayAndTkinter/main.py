import logging
import random
import tkinter as tk
import tkinter.messagebox as tk_messagebox

ROW_COUNT = 4
COL_COUNT = 4
MINSIZE_BUTTON = 64


class Application(tk.Frame):
    """
    Application frame, grouping all other elements
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.actions_bar = ActionsBar(self)
        self.game_grid = GameOf15(self)
        self.actions_bar.pack(fill="x")
        self.game_grid.pack(fill="both", expand=1)

    def restart_game(self):
        self.game_grid.reorder_buttons()


class ActionsBar(tk.Frame):
    """
    Contains action buttons
    """

    def __init__(self, master: Application, *args, **kw):
        super().__init__(master, *args, **kw)
        self.restart_game = tk.Button(self, text="New", command=self.master.restart_game)
        self.quit = tk.Button(self, text="Exit", fg="red", command=self.master.quit)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.restart_game.grid(row=0, column=0)
        self.quit.grid(row=0, column=1)


class GameButton(tk.Button):
    def __init__(self, number, *args, **kw):
        super().__init__(*args, **kw)
        self.number = number


class GameOf15(tk.Frame):
    """
    Contains grid with the game itself
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.buttons = [GameButton(btn_index, self, text=f"{btn_index}",
                                   command=self.get_btn_command(btn_index)) for btn_index in
                        range(1, COL_COUNT * ROW_COUNT)]
        self.buttons.append(None)
        for col in range(COL_COUNT):
            self.grid_columnconfigure(col, weight=1, minsize=MINSIZE_BUTTON)
        for row in range(ROW_COUNT):
            self.grid_rowconfigure(row, weight=1, minsize=MINSIZE_BUTTON)
        self.reorder_buttons()

    def get_btn_command(self, btn_number):
        def try_move():
            for btn in self.buttons:
                if btn is not None and btn.number == btn_number:
                    target_button = btn
                    break
            else:
                return
            gr_info = target_button.grid_info()
            my_row, my_col = int(gr_info["row"]), int(gr_info["column"])  # we could find this info other way
            empty_pos = self.buttons.index(None)
            empty_row, empty_col = empty_pos // COL_COUNT, empty_pos % COL_COUNT
            if abs(empty_row - my_row) + abs(empty_col - my_col) == 1:
                target_button.grid(row=empty_row, column=empty_col, sticky=tk.NSEW)
                self.buttons[empty_pos] = target_button
                self.buttons[my_row * COL_COUNT + my_col] = None
                if self.check_win():
                    logging.info("User won! Restarting...")
                    self.restart_won_game()

        return try_move

    def check_win(self):
        for i in range(1, len(self.buttons) - 1):
            if None in (self.buttons[i], self.buttons[i - 1]) or \
                    self.buttons[i].number != self.buttons[i - 1].number + 1:
                return False
        return self.buttons[-1] is None

    def reorder_buttons(self):

        def is_solvable():
            n = 0
            for _i in range(len(self.buttons) - 1):
                if self.buttons[_i] is None:
                    n += _i // COL_COUNT + 1
                    continue
                for _j in range(_i + 1, len(self.buttons)):
                    if self.buttons[_j] is not None and self.buttons[_i].number > self.buttons[_j].number:
                        n += 1
            return n % 2 == 0

        random.shuffle(self.buttons)
        while not is_solvable():
            logging.info("Regenerating grid, current grid is unsolvable")
            random.shuffle(self.buttons)
        logging.info("Generated new grid")
        for i in range(len(self.buttons)):
            if self.buttons[i] is None:
                continue
            self.buttons[i].grid(row=i // COL_COUNT, column=i % COL_COUNT, sticky=tk.NSEW)

    def restart_won_game(self):
        tk_messagebox.showinfo(title="Info", message="You won!")
        self.reorder_buttons()


def main():
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.attributes('-type', 'dialog')  # this is important in tiling WM
    root.title("Game of Fifteen")
    app = Application(master=root)
    app.pack(fill="both", expand=1)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    app.mainloop()


if __name__ == '__main__':
    main()
