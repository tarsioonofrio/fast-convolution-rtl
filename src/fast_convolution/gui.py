import tkinter as tk
from tkinter import ttk

from fast_convolution import commands
from fast_convolution.utils import file_init


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast Convolution")
        self.geometry("400x400")

        self.dimension = tk.StringVar()
        self.init_dict = {}
        self.init_dict = {}
        self.build_dict = {}
        self.init()

    def init(self):
        # Limpa a janela antes de carregar a nova tela
        for widget in self.winfo_children():
            widget.destroy()

        if file_init.exists():
            label = tk.Label(self, text="init.json existis, fconv model already initialized")
            label.pack(pady=10)
        else:
            label = tk.Label(self, text="Escolha entre 1 e 2 dimensões:")
            label.pack(pady=10)

            choice_menu = ttk.Combobox(self, textvariable=self.dimension)
            choice_menu['values'] = ["1", "2"]
            choice_menu.pack(pady=10)

            btn_next = tk.Button(self, text="Próximo", command=self.build)
            btn_next.pack(pady=10)

    def build(self):
        dimension = self.dimension.get()

        for widget in self.winfo_children():
            widget.destroy()

        if dimension == '1':
            self.build_dict['in'] = tk.StringVar()
            self.build_dict['out'] = tk.StringVar()
            self.build_dict['weights'] = tk.StringVar(value='3')

            tk.Label(self, text="in:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['in']).pack(pady=5)

            tk.Label(self, text="out:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['out']).pack(pady=5)

            tk.Label(self, text="weights:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['weights']).pack(pady=5)

        elif dimension == '2':
            self.build_dict['in1'] = tk.StringVar()
            self.build_dict['in2'] = tk.StringVar()
            self.build_dict['out1'] = tk.StringVar()
            self.build_dict['out2'] = tk.StringVar()
            self.build_dict['weights1'] = tk.StringVar()
            self.build_dict['weights2'] = tk.StringVar()

            tk.Label(self, text="in1:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['in1']).pack(pady=5)

            tk.Label(self, text="in2:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['in2']).pack(pady=5)

            tk.Label(self, text="out1:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['out1']).pack(pady=5)

            tk.Label(self, text="out2:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['out2']).pack(pady=5)

            tk.Label(self, text="weights1:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['weights1']).pack(pady=5)

            tk.Label(self, text="weights2:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['weights2']).pack(pady=5)

        btn_next = tk.Button(self, text="Próximo", command=self.others)
        btn_next.pack(pady=10)

    def others(self):
        for widget in self.winfo_children():
            widget.destroy()

        dimension = self.dimension.get()
        inn_ = self.build_dict['in'].get()
        out_ = self.build_dict['out'].get()
        weights_ = self.build_dict['weights'].get()

        dim = int(dimension) if dimension.isdigit() else None
        inn = int(inn_) if inn_.isdigit() else None
        out = int(out_) if out_.isdigit() else None
        weights = int(weights_) if weights_.isdigit() else None

        commands.cmd_init(
            dim,
            inn if inn != 0 else None,
            out if out != 0 else None,
            weights if weights != 0 else None,
        )
        notebook = ttk.Notebook(self)
        notebook.pack(expand=1, fill='both')

        if dimension == '1':
            self.add_tab(notebook, "Aba 1")
            self.add_tab(notebook, "Aba 2")
        elif dimension == '2':
            self.add_tab(notebook, "Aba 1")
            self.add_tab(notebook, "Aba 2")
            self.add_tab(notebook, "Aba 3")

    def add_tab(self, notebook, title):
        frame = tk.Frame(notebook)
        notebook.add(frame, text=title)

        label = tk.Label(frame, text=f"Conteúdo da {title}")
        label.pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
