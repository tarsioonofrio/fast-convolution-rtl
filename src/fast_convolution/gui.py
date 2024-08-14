import tkinter as tk
from tkinter import ttk


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast Convolution")
        self.geometry("400x400")

        self.choice_var = tk.StringVar()
        self.init_dict = {}
        self.build_dict = {}

        self.init()

    def init(self):
        # Limpa a janela antes de carregar a nova tela
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Escolha entre 1D e 2D:")
        label.pack(pady=10)

        self.choice_menu = ttk.Combobox(self, textvariable=self.choice_var)
        self.choice_menu['values'] = ["1D", "2D"]
        self.choice_menu.pack(pady=10)

        btn_next = tk.Button(self, text="Próximo", command=self.build)
        btn_next.pack(pady=10)

    def build(self):
        choice = self.choice_var.get()

        for widget in self.winfo_children():
            widget.destroy()

        if choice == "1D":
            self.build_dict['in'] = tk.StringVar()
            self.build_dict['out'] = tk.StringVar()
            self.build_dict['weights'] = tk.StringVar()

            tk.Label(self, text="in:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['in']).pack(pady=5)

            tk.Label(self, text="out:").pack(pady=5)
            tk.Entry(self, textvariable=self.build_dict['out']).pack(pady=5)

            tk.Label(self, text="weights:").pack(pady=5)
            tk.Entry(self, textvariable=self.init_dict['weights']).pack(pady=5)
        elif choice == "2D":
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
        choice = self.choice_var.get()

        for widget in self.winfo_children():
            widget.destroy()

        notebook = ttk.Notebook(self)
        notebook.pack(expand=1, fill='both')

        if choice == "1D":
            self.add_tab(notebook, "Aba 1")
            self.add_tab(notebook, "Aba 2")
        elif choice == "2D":
            self.add_tab(notebook, "Aba 1")
            self.add_tab(notebook, "Aba 2")
            self.add_tab(notebook, "Aba 3")

    def add_tab(self, notebook, title):
        frame = tk.Frame(notebook)
        notebook.add(frame, text=title)

        label = tk.Label(frame, text=f"Conteúdo da {title}")
        label.pack(pady=10)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
