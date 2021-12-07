import os

import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox, StringVar

from pearson_test import NormPearsonChiSquaredTest, BadInput


class MainWindow(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.window_width, self.window_height = 800, 400
        self.root.minsize(800, 400)
        self.root.title('Критерий хи-квадрат Пирсона')
        root_width, root_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        left = (root_width - self.window_width) // 2
        top = (root_height - self.window_height) // 2
        self.root.geometry(f'{self.window_width}x{self.window_height}+{left}+{top}')

        self.f_contols = tk.Frame(master=self.root, width=self.window_width // 2)
        self.f_indicators = tk.Frame(master=self.root, width=self.window_width // 2)

        self.btn_create = tk.Button(
            self.f_contols,
            text='Загрузить выборку\nи рассчитать',
            command=self.on_open
        )
        self.n_intervals = StringVar()
        self.alpha = StringVar()
        self.n_intervals_input = tk.Spinbox(self.f_contols, from_=4, to=1000, increment=1, textvariable=self.n_intervals)
        self.n_intervals_label = tk.Label(self.f_contols, text='Число интервалов:')
        self.alpha_input = tk.Spinbox(self.f_contols, from_=0, to=1, increment=0.01, textvariable=self.alpha)
        self.alpha_label = tk.Label(self.f_contols, text='Уровень значимости:')
        self.btn_export = tk.Button(
            self.f_contols,
            text='Сохранить отчет',
            command=self.on_export
        )
        self.output = tk.Text(self.f_indicators, wrap=tk.WORD)
        self.reset_output()

        self.n_intervals.set(10)
        self.alpha.set(0.05)

        self.f_contols.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
        self.f_indicators.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.btn_create.pack(side=tk.TOP, padx=10, pady=10)
        self.n_intervals_label.pack(side=tk.TOP, padx=10, pady=10)
        self.n_intervals_input.pack(side=tk.TOP, padx=10, pady=10)
        self.alpha_label.pack(side=tk.TOP, padx=10, pady=10)
        self.alpha_input.pack(side=tk.TOP, padx=10, pady=10)
        self.btn_export.pack(side=tk.TOP, padx=10, pady=10)

        self.output.pack(side=tk.TOP, padx=10, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def reset_output(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete('1.0', 'end')
        self.output.insert(tk.END, 'Здесь будет отображен результат теста.')
        self.output.config(state=tk.DISABLED)

    def on_close(self):
        plt.close()
        self.root.destroy()

    def on_export(self):
        filename = fd.asksaveasfilename(filetypes=[('Text file', '*.txt')])
        if not filename:
            return
        if not filename.endswith('.txt'):
            filename += '.txt'
        with open(filename, 'w') as fout:
            fout.write(self.output.get('1.0', tk.END))

    def on_open(self):
        filename = fd.askopenfilename(filetypes=[('Linebreak separated txt values',  '*.txt')])
        if not filename:
            return
        try:
            n_intervals = int(self.n_intervals.get())
        except ValueError:
            messagebox.showerror(
                'Неверный ввод',
                'Число интервалов должен быть целым числом.'
            )
            self.reset_output()
            return
        try:
            alpha = float(self.alpha.get())
        except ValueError:
            messagebox.showerror(
                'Неверный ввод',
                'Уровень значимости должен быть вещественным числом'
            )
            self.reset_output()
            return
        try:
            pearson_test = NormPearsonChiSquaredTest(filename, n_intervals, alpha)
        except BadInput:
            messagebox.showerror(
                'Неверный ввод',
                'На входе ожидается текстовый файл с выборкой, '
                'где каждый элемен расположен на отдельной строке и явялется коректным '
                'вещественным числом.'
            )
            self.reset_output()
            return
        h1_msg = 'Нулевая гипотеза H0 была отвергнута, нет оснований полагать, ' \
                 'что выборка принадлежит нормальному распределению.'
        h0_msg = 'Нулевая гипотеза H0 не может быть отвергнута, есть основания полагать, ' \
                 'что выборка принадлежит нормальному распределению.'
        stats_msg = '\n\n' \
                    '=== Промежуточные результаты ===\n' \
                    'Выборочное среднее: {:.6f}\n' \
                    'Дисперсия: {:.6f}\n' \
                    'Выборочное стандартное отклонение: {:.6f}\n' \
                    'Несмещенная оценка стандартного отклонения: {:.6f}\n' \
                    'Границы интервалов: {}\n' \
                    'Наблюдаемые частоты: {}\n' \
                    'Теоретические частоты: {}\n' \
                    'Длина интервала: {:.6f}\n' \
                    'Хи квадрат наблюдаемое: {:.6f}\n' \
                    'Хи квадрат критическое: {:.6f}'
        res = h1_msg if pearson_test.evaluate_chisq() else h0_msg
        res += stats_msg.format(
            pearson_test.stats['mean'],
            pearson_test.stats['var'],
            pearson_test.stats['std'],
            pearson_test.stats['std2'],
            ', '.join((f'{i:.3f}' for i in pearson_test.bins)),
            ', '.join((f'{i:.3f}' for i in pearson_test.hist)),
            ', '.join((f'{i:.3f}' for i in pearson_test.n_dash_list)),
            pearson_test.h,
            pearson_test.chisq,
            pearson_test.chisq_crit
        )
        self.output.config(state=tk.NORMAL)
        self.output.delete('1.0', 'end')
        self.output.insert(tk.END, res)
        self.output.config(state=tk.DISABLED)
        plt.close()
        plt.figure()
        plt.suptitle(os.path.basename(filename))
        plt.hist(pearson_test.samples, bins=n_intervals)
        plt.show()


if __name__ == '__main__':
    rootObj = tk.Tk()
    app = MainWindow(rootObj)
    app.pack()
    rootObj.mainloop()
