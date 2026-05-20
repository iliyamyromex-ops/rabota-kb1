import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "expenses.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class ExpenseTrackerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("750x600")

        self.expenses = load_data()

        form_frame = tk.LabelFrame(root, text="Добавить расход")
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Сумма:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Категория:").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.category_combobox = ttk.Combobox(
            form_frame, values=["Еда", "Транспорт", "Развлечения", "Другое"]
        )
        self.category_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.category_combobox.current(0)

        tk.Label(form_frame, text="Дата (ДД.ММ.ГГГГ):").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.date_entry = tk.Entry(form_frame)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        add_btn = tk.Button(
            form_frame, text="Добавить расход", command=self.add_expense
        )
        add_btn.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        filter_frame = tk.LabelFrame(root, text="Фильтрация и Анализ")
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.filter_category_combobox = ttk.Combobox(
            filter_frame,
            values=["Все", "Еда", "Транспорт", "Развлечения", "Другое"],
        )
        self.filter_category_combobox.grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )
        self.filter_category_combobox.current(0)

        tk.Label(filter_frame, text="С (ДД.ММ.ГГГГ):").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.start_date_entry = tk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(filter_frame, text="По (ДД.ММ.ГГГГ):").grid(
            row=0, column=4, padx=5, pady=5, sticky="e"
        )
        self.end_date_entry = tk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        filter_btn = tk.Button(
            filter_frame, text="Применить", command=self.refresh_table
        )
        filter_btn.grid(row=0, column=6, padx=10, pady=5)

        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")

        self.tree.column("amount", width=150, anchor="center")
        self.tree.column("category", width=200, anchor="center")
        self.tree.column("date", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        summary_frame = tk.Frame(root)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.total_label = tk.Label(
            summary_frame,
            text="Итого за выбранный период: 0.00",
            font=("Arial", 12, "bold"),
        )
        self.total_label.pack(side="right")

        self.refresh_table()

        delete_btn = tk.Button(
            summary_frame, text="Удалить выбранное", command=self.delete_expense
        )
        delete_btn.pack(side="left")

    def validate_inputs(self, amount_str, date_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Сумма должна быть положительным числом."
            )
            return None

        try:
            valid_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ."
            )
            return None

        return amount, valid_date.strftime("%d.%m.%Y")

    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_combobox.get()
        date_str = self.date_entry.get().strip()

        validated = self.validate_inputs(amount_str, date_str)
        if not validated:
            return

        amount, final_date = validated

        new_expense = {"amount": amount, "category": category, "date": final_date}

        self.expenses.append(new_expense)
        save_data(self.expenses)

        self.amount_entry.delete(0, tk.END)

        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_category = self.filter_category_combobox.get()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()

        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
            except ValueError:
                messagebox.showerror(
                    "Ошибка",
                    "Неверный формат начальной даты фильтра (ДД.ММ.ГГГГ).",
                )
                return

        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%d.%m.%Y").date()
            except ValueError:
                messagebox.showerror(
                    "Ошибка",
                    "Неверный формат конечной даты фильтра (ДД.ММ.ГГГГ).",
                )
                return

        total_sum = 0.0

        for idx, exp in enumerate(self.expenses):
            exp_date = datetime.strptime(exp["date"], "%d.%m.%Y").date()

            if (
                filter_category != "Все"
                and exp["category"] != filter_category
            ):
                continue
            if start_date and exp_date < start_date:
                continue
            if end_date and exp_date > end_date:
                continue

            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(f"{exp['amount']:.2f}", exp["category"], exp["date"]),
            )
            total_sum += exp["amount"]

        self.total_label.config(
            text=f"Итого за выбранный период: {total_sum:.2f}"
        )

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Предупреждение", "Выберите запись для удаления."
            )
            return

        idx_to_delete = int(selected_item[0])

        filtered_category = self.filter_category_combobox.get()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()

        if (
            filtered_category != "Все"
            or start_date_str
            or end_date_str
        ):
            messagebox.showinfo(
                "Информация",
                "Сбросьте фильтры перед удалением записей для корректной работы.",
            )
            return

        del self.expenses[idx_to_delete]
        save_data(self.expenses)
        self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
      
