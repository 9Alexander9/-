import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье", "Одежда", "Другое"]

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Учет расходов")
        self.root.geometry("900x600")

        self.expenses = self.load_data()
 
        input_frame = tk.LabelFrame(root, text="Новый расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5)
        self.entry_amount = tk.Entry(input_frame, width=15)
        self.entry_amount.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5)
        self.combo_category = ttk.Combobox(input_frame, values=CATEGORIES, state="readonly", width=15)
        self.combo_category.set(CATEGORIES[0])
        self.combo_category.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5)
        self.entry_date = tk.Entry(input_frame, width=15)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.entry_date.grid(row=0, column=5, padx=5)

        btn_add = tk.Button(input_frame, text="Добавить", command=self.add_expense, bg="#4CAF50", fg="white")
        btn_add.grid(row=0, column=6, padx=10)

        control_frame = tk.Frame(root)
        control_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(control_frame, text="Фильтр по категории:").pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="Все")
        combo_filter = ttk.Combobox(control_frame, textvariable=self.filter_var, values=["Все"] + CATEGORIES, state="readonly", width=15)
        combo_filter.pack(side="left", padx=5)
        combo_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        self.lbl_total = tk.Label(control_frame, text="Итого: 0.00 руб.", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_total.pack(side="right", padx=10)

        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Date", "Category", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Category", text="Категория")
        self.tree.heading("Amount", text="Сумма")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Category", width=150, anchor="w")
        self.tree.column("Amount", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_del = tk.Button(root, text="Удалить выбранное", command=self.delete_expense, bg="#f44336", fg="white")
        btn_del.pack(pady=5)

        self.refresh_table()

    def load_data(self):
        """Загружает расходы из JSON файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_data(self):
        """Сохраняет текущий список расходов в JSON"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def validate_inputs(self):
        """Проверяет корректность ввода суммы и даты"""
        amount_str = self.entry_amount.get().strip()
        date_str = self.entry_date.get().strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Введите корректную положительную сумму.")
            return None

        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            return None

        return amount, date_str

    def add_expense(self):
        """Добавляет новую запись"""
        result = self.validate_inputs()
        if not result:
            return
        
        amount, date_str = result
        category = self.combo_category.get()

        new_id = 1
        if self.expenses:
            new_id = max([item['id'] for item in self.expenses]) + 1

        new_expense = {
            "id": new_id,
            "date": date_str,
            "category": category,
            "amount": amount
        }

        self.expenses.append(new_expense)
        self.save_data()
        self.refresh_table()
        
        self.entry_amount.delete(0, tk.END)

    def delete_expense(self):
        """Удаляет выбранную запись"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return

        item_values = self.tree.item(selected_item[0])['values']
        item_id = item_values[0]

        self.expenses = [exp for exp in self.expenses if exp['id'] != item_id]
        self.save_data()
        self.refresh_table()

    def refresh_table(self):
        """Обновляет таблицу и считает итог с учетом фильтра"""
     
        for row in self.tree.get_children():
            self.tree.delete(row)

        filter_cat = self.filter_var.get()
        total_sum = 0.0

        sorted_expenses = sorted(self.expenses, key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y"), reverse=True)

        for exp in sorted_expenses:

            if filter_cat != "Все" and exp['category'] != filter_cat:
                continue

            self.tree.insert("", "end", values=(
                exp['id'],
                exp['date'],
                exp['category'],
                f"{exp['amount']:.2f}"
            ))
            total_sum += exp['amount']

        self.lbl_total.config(text=f"Итого: {total_sum:.2f} руб.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()