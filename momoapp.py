"""
MoMo Wallet Pro - Lab 3 (Python OOP)
Name: ADANE GODFRED AMOFAH
Index No: 2526404689

A desktop mobile-money simulator built with:
- Classes and objects
- Inheritance and polymorphism
- Custom exceptions
- JSON data storage
- Modern Tkinter FinTech GUI
- PIN-protected transactions
- Personal and merchant accounts
"""

import csv
import json
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation


# Always store data beside this Python file. This works on Windows.
DATA_FILE = Path(__file__).resolve().with_name("momo_data.json")

# Modern FinTech Color Palette
BG = "#F1F5F9"
SIDEBAR_BG = "#0B132B"
SIDEBAR_CARD = "#162246"
CARD = "#FFFFFF"
CARD_ALT = "#F8FAFC"
NAVY = "#0F172A"
GOLD = "#F59E0B"
GOLD_DARK = "#D97706"
GREEN = "#10B981"
GREEN_DARK = "#059669"
BLUE = "#2563EB"
BLUE_DARK = "#1D4ED8"
PURPLE = "#7C3AED"
PURPLE_DARK = "#6D28D9"
SLATE = "#475569"
SLATE_DARK = "#334155"
TEXT = "#1E293B"
MUTED = "#64748B"
RED = "#EF4444"
BORDER = "#E2E8F0"


# --- Custom Exceptions ---
class MoMoError(Exception):
    """Base exception for MoMo Wallet operations."""


class InvalidAmountError(MoMoError):
    """Raised when a transaction amount is invalid or non-positive."""


class InsufficientFundsError(MoMoError):
    """Raised when an account balance cannot cover the transaction and fee."""


class InvalidPinError(MoMoError):
    """Raised when PIN verification fails."""


class AccountNotFoundError(MoMoError):
    """Raised when a target wallet account does not exist."""


def money(value):
    return f"GHS {float(value):,.2f}"


def pin_hash(pin):
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def valid_phone(phone):
    return phone.isdigit() and len(phone) == 10 and phone.startswith("0")


def to_amount(value):
    try:
        amount = Decimal(value.strip())
        if not amount.is_finite() or amount <= 0:
            raise InvalidAmountError("Enter an amount greater than zero.")
        return amount.quantize(Decimal("0.01"))
    except (InvalidOperation, AttributeError) as exc:
        raise InvalidAmountError("Enter a valid numeric amount greater than zero.") from exc


class Account:
    """Base class for wallet accounts."""

    def __init__(self, name, phone, balance=0, pin_digest=None, account_type="Personal"):
        self.name = name
        self.phone = phone
        self.balance = Decimal(str(balance))
        self.pin_digest = pin_digest or pin_hash("1234")
        self.account_type = account_type

    def verify_pin(self, pin):
        return pin_hash(pin) == self.pin_digest

    def transaction_fee(self, amount):
        return Decimal("0.00")

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError("Your wallet balance is too low.")
        self.balance -= amount

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "balance": str(self.balance),
            "pin_hash": self.pin_digest,
            "account_type": self.account_type,
        }


class PersonalAccount(Account):
    def __init__(self, name, phone, balance=0, pin_digest=None):
        super().__init__(name, phone, balance, pin_digest, "Personal")


class MerchantAccount(Account):
    """Merchant wallets pay a 1% fee on outgoing transfers."""

    def __init__(self, name, phone, balance=0, pin_digest=None):
        super().__init__(name, phone, balance, pin_digest, "Merchant")

    def transaction_fee(self, amount):
        return (amount * Decimal("0.01")).quantize(Decimal("0.01"))


class Transaction:
    def __init__(self, tx_type, amount, sender="", receiver="", fee=0, note=""):
        self.tx_type = tx_type
        self.amount = Decimal(str(amount))
        self.sender = sender
        self.receiver = receiver
        self.fee = Decimal(str(fee))
        self.note = note
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "type": self.tx_type,
            "amount": str(self.amount),
            "sender": self.sender,
            "receiver": self.receiver,
            "fee": str(self.fee),
            "note": self.note,
            "date": self.date,
        }


class MoMoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MoMo Wallet Pro • Digital Finance Simulator")
        self.root.geometry("1240x790")
        self.root.minsize(1020, 680)
        self.root.configure(bg=BG)

        self.accounts = {}
        self.transactions = []
        self.selected_phone = None
        self.hide_balance = False

        self.load_data()
        self.build_style()
        self.build_ui()
        self.refresh_all()

    def build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=CARD,
            fieldbackground=CARD,
            foreground=TEXT,
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background="#F1F5F9",
            foreground=MUTED,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padding=(8, 8),
        )
        style.map(
            "Treeview",
            background=[("selected", "#E0F2FE")],
            foreground=[("selected", NAVY)],
        )
        style.configure(
            "Modern.TCombobox",
            padding=8,
            fieldbackground="white",
            background="white",
            foreground=NAVY,
        )

    def load_data(self):
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("Invalid JSON root format; expected a dictionary.")

                for item in data.get("accounts", []):
                    if not isinstance(item, dict):
                        continue
                    digest = item.get("pin_hash") or pin_hash("1234")
                    cls = MerchantAccount if item.get("account_type") == "Merchant" else PersonalAccount
                    account = cls(item["name"], item["phone"], item.get("balance", 0), digest)
                    self.accounts[account.phone] = account

                raw_txs = data.get("transactions", [])
                self.transactions = raw_txs if isinstance(raw_txs, list) else []

            except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError, AttributeError, InvalidOperation):
                messagebox.showwarning(
                    "Data file",
                    "The saved data file had an incompatible format. A fresh wallet file will be created."
                )
                self.accounts = {}
                self.transactions = []

        if not self.accounts:
            demos = [
                PersonalAccount("Ama Mensah", "0241112222", 500),
                PersonalAccount("Kofi Boateng", "0553334444", 200),
                MerchantAccount("Akosua Darko - Auntie Akos Chop Bar", "0205556666", 1000),
            ]
            self.accounts = {a.phone: a for a in demos}
            self.save_data()

    def save_data(self):
        data = {
            "accounts": [account.to_dict() for account in self.accounts.values()],
            "transactions": self.transactions,
        }
        try:
            DATA_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Save error", f"Could not save wallet data:\n{exc}")

    def add_hover(self, widget, normal_bg, hover_bg):
        widget.bind("<Enter>", lambda _e: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda _e: widget.config(bg=normal_bg))

    def build_ui(self):
        # Main Split Layout: Dark FinTech Left Sidebar + Clean Light Main Workspace
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True)

        # --- LEFT SIDEBAR ---
        sidebar = tk.Frame(shell, bg=SIDEBAR_BG, width=360)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Brand Header
        brand_row = tk.Frame(sidebar, bg=SIDEBAR_BG)
        brand_row.pack(fill="x", padx=24, pady=(24, 18))

        logo_badge = tk.Label(
            brand_row, text="M", bg=GOLD, fg=SIDEBAR_BG,
            font=("Segoe UI", 15, "bold"), width=3, height=1
        )
        logo_badge.pack(side="left")

        brand_text = tk.Frame(brand_row, bg=SIDEBAR_BG)
        brand_text.pack(side="left", padx=12)
        tk.Label(
            brand_text, text="MoMo Wallet Pro", bg=SIDEBAR_BG, fg="white",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")
        tk.Label(
            brand_text, text="DIGITAL FINANCE SIMULATOR", bg=SIDEBAR_BG, fg="#94A3B8",
            font=("Segoe UI", 7, "bold")
        ).pack(anchor="w")

        # Active Wallet Selector
        tk.Label(
            sidebar, text="ACTIVE WALLET ACCOUNT", bg=SIDEBAR_BG, fg="#94A3B8",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=24, pady=(4, 6))

        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(
            sidebar, textvariable=self.account_var,
            state="readonly", font=("Segoe UI", 10), style="Modern.TCombobox"
        )
        self.account_combo.pack(fill="x", padx=24, pady=(0, 18))
        self.account_combo.bind("<<ComboboxSelected>>", self.on_account_selected)

        # Digital Debit / Wallet Card
        wallet_card = tk.Frame(
            sidebar, bg=SIDEBAR_CARD, highlightbackground="#2A3B6E", highlightthickness=1
        )
        wallet_card.pack(fill="x", padx=24, pady=(0, 18))

        card_top = tk.Frame(wallet_card, bg=SIDEBAR_CARD)
        card_top.pack(fill="x", padx=18, pady=(16, 8))

        self.type_badge = tk.Label(
            card_top, text="PERSONAL", bg="#1E3A8A", fg="#93C5FD",
            font=("Segoe UI", 8, "bold"), padx=9, pady=3
        )
        self.type_badge.pack(side="left")

        self.eye_btn = tk.Button(
            card_top, text="Hide", command=self.toggle_balance,
            bg="#233363", fg="#CBD5E1", activebackground="#2E427D",
            activeforeground="white", relief="flat", font=("Segoe UI", 8, "bold"),
            padx=10, pady=2, cursor="hand2"
        )
        self.eye_btn.pack(side="right")

        tk.Label(
            wallet_card, text="AVAILABLE BALANCE", bg=SIDEBAR_CARD, fg="#94A3B8",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=18, pady=(6, 2))

        self.balance_label = tk.Label(
            wallet_card, text="GHS 0.00", bg=SIDEBAR_CARD, fg="white",
            font=("Segoe UI", 24, "bold")
        )
        self.balance_label.pack(anchor="w", padx=18)

        divider = tk.Frame(wallet_card, bg="#253668", height=1)
        divider.pack(fill="x", padx=18, pady=(14, 10))

        self.account_name_label = tk.Label(
            wallet_card, text="", bg=SIDEBAR_CARD, fg="#E2E8F0",
            font=("Segoe UI", 10, "bold"), wraplength=275, justify="left"
        )
        self.account_name_label.pack(anchor="w", padx=18)

        self.account_phone_label = tk.Label(
            wallet_card, text="", bg=SIDEBAR_CARD, fg=GOLD,
            font=("Consolas", 10, "bold")
        )
        self.account_phone_label.pack(anchor="w", padx=18, pady=(2, 16))

        # Quick Actions Section
        tk.Label(
            sidebar, text="QUICK TRANSACTIONS", bg=SIDEBAR_BG, fg="#94A3B8",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=24, pady=(2, 8))

        self.sidebar_button(sidebar, "＋   Deposit Money", self.deposit_window, GREEN, GREEN_DARK)
        self.sidebar_button(sidebar, "↑    Transfer Money", self.transfer_window, PURPLE, PURPLE_DARK)
        self.sidebar_button(sidebar, "↓    Withdraw Money", self.withdraw_window, BLUE, BLUE_DARK)
        self.sidebar_button(sidebar, "⇩   Export CSV Statement", self.export_statement, SLATE, SLATE_DARK)

        # Fee Notice Pill
        fee_box = tk.Frame(sidebar, bg="#131E3E", highlightbackground="#223261", highlightthickness=1)
        fee_box.pack(fill="x", padx=24, pady=(14, 0))
        tk.Label(
            fee_box,
            text="ℹ  Personal transfers are free. Merchant wallets incur a 1% outgoing transfer fee.",
            bg="#131E3E", fg="#94A3B8", font=("Segoe UI", 8),
            wraplength=280, justify="left", padx=12, pady=10
        ).pack(anchor="w")

        # Student Footer in Sidebar
        tk.Label(
            sidebar, text="ADANE GODFRED AMOFAH • 2526404689",
            bg=SIDEBAR_BG, fg="#475569", font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", pady=14)

        # --- RIGHT MAIN WORKSPACE ---
        main = tk.Frame(shell, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=26, pady=22)

        # Top Action Bar
        topbar = tk.Frame(main, bg=BG)
        topbar.pack(fill="x", pady=(0, 18))

        title_col = tk.Frame(topbar, bg=BG)
        title_col.pack(side="left")
        tk.Label(
            title_col, text="Dashboard Overview", bg=BG, fg=NAVY,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")
        tk.Label(
            title_col, text="Manage mobile wallets, authorize PIN transfers, and audit ledger activity",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w")

        reg_btn = tk.Button(
            topbar, text="+  Register New Wallet", command=self.create_account_window,
            bg=GOLD, fg=SIDEBAR_BG, activebackground=GOLD_DARK,
            activeforeground=SIDEBAR_BG, relief="flat", padx=18, pady=11,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        reg_btn.pack(side="right", pady=4)
        self.add_hover(reg_btn, GOLD, GOLD_DARK)

        # KPI Metric Cards Row
        stats = tk.Frame(main, bg=BG)
        stats.pack(fill="x", pady=(0, 18))
        self.stat_accounts = self.stat_card(stats, "REGISTERED WALLETS", "0", "#0284C7", padx=(0, 12))
        self.stat_transactions = self.stat_card(stats, "TOTAL TRANSACTIONS", "0", "#7C3AED", padx=(0, 12))
        self.stat_volume = self.stat_card(stats, "TOTAL LEDGER VOLUME", "GHS 0.00", "#059669", padx=(0, 0))

        # Transaction History Card
        history_card = tk.Frame(main, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        history_card.pack(fill="both", expand=True)

        top = tk.Frame(history_card, bg=CARD)
        top.pack(fill="x", padx=20, pady=(18, 12))

        left_hdr = tk.Frame(top, bg=CARD)
        left_hdr.pack(side="left")
        tk.Label(
            left_hdr, text="Transaction Ledger", bg=CARD, fg=NAVY,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")
        self.filter_count_label = tk.Label(
            left_hdr, text="Showing all transactions", bg=CARD, fg=MUTED,
            font=("Segoe UI", 8)
        )
        self.filter_count_label.pack(anchor="w")

        # Search Box Container
        search_box = tk.Frame(top, bg="#F8FAFC", highlightbackground=BORDER, highlightthickness=1)
        search_box.pack(side="right", pady=2)
        tk.Label(search_box, text="🔍", bg="#F8FAFC", fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(8, 4))

        self.search_var = tk.StringVar()
        search = tk.Entry(
            search_box, textvariable=self.search_var, font=("Segoe UI", 9),
            bg="#F8FAFC", fg=TEXT, relief="flat", width=26
        )
        search.pack(side="left", ipady=6)
        search.bind("<KeyRelease>", lambda _e: self.refresh_history())

        clear_btn = tk.Button(
            search_box, text="✕", command=self.clear_search,
            bg="#F8FAFC", fg=MUTED, relief="flat", font=("Segoe UI", 8, "bold"),
            cursor="hand2", padx=6
        )
        clear_btn.pack(side="left")

        # Treeview + Scrollbar Container
        table_wrap = tk.Frame(history_card, bg=CARD)
        table_wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        columns = ("date", "type", "sender", "receiver", "amount", "fee")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        headings = {
            "date": "DATE & TIME",
            "type": "TYPE",
            "sender": "SENDER",
            "receiver": "RECEIVER",
            "amount": "AMOUNT",
            "fee": "FEE",
        }
        widths = {
            "date": 155,
            "type": 105,
            "sender": 130,
            "receiver": 130,
            "amount": 120,
            "fee": 90,
        }
        anchors = {
            "date": "w",
            "type": "center",
            "sender": "w",
            "receiver": "w",
            "amount": "e",
            "fee": "e",
        }

        for col in columns:
            self.tree.heading(col, text=headings[col], anchor=anchors[col])
            self.tree.column(col, width=widths[col], anchor=anchors[col])

        # Row Styling Tags
        self.tree.tag_configure("deposit", foreground="#059669", background="#FFFFFF")
        self.tree.tag_configure("deposit_alt", foreground="#059669", background="#F8FAFC")
        self.tree.tag_configure("transfer", foreground="#6D28D9", background="#FFFFFF")
        self.tree.tag_configure("transfer_alt", foreground="#6D28D9", background="#F8FAFC")
        self.tree.tag_configure("withdrawal", foreground="#1D4ED8", background="#FFFFFF")
        self.tree.tag_configure("withdrawal_alt", foreground="#1D4ED8", background="#F8FAFC")

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        # Bottom Status Bar
        footer = tk.Label(
            main, text=f"Local JSON Storage Active • File: {DATA_FILE.name}",
            bg=BG, fg=MUTED, font=("Segoe UI", 8)
        )
        footer.pack(anchor="e", pady=(8, 0))

    def sidebar_button(self, parent, label, command, color, hover_color):
        btn = tk.Button(
            parent, text=label, command=command, bg=color, fg="white",
            activeforeground="white", activebackground=hover_color,
            relief="flat", font=("Segoe UI", 10, "bold"), anchor="w",
            padx=18, pady=10, cursor="hand2"
        )
        btn.pack(fill="x", padx=24, pady=4)
        self.add_hover(btn, color, hover_color)
        return btn

    def stat_card(self, parent, label, value, accent_color, padx=(0, 10)):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=padx)

        top_strip = tk.Frame(card, bg=accent_color, height=4)
        top_strip.pack(fill="x")

        tk.Label(
            card, text=label, bg=CARD, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=18, pady=(14, 4))

        value_label = tk.Label(
            card, text=value, bg=CARD, fg=NAVY,
            font=("Segoe UI", 18, "bold")
        )
        value_label.pack(anchor="w", padx=18, pady=(0, 16))
        return value_label

    def toggle_balance(self):
        self.hide_balance = not self.hide_balance
        self.eye_btn.config(text="Show" if self.hide_balance else "Hide")
        self.refresh_all()

    def clear_search(self):
        self.search_var.set("")
        self.refresh_history()

    def refresh_all(self):
        choices = [f"{a.name}  |  {a.phone}" for a in self.accounts.values()]
        self.account_combo["values"] = choices

        if self.selected_phone not in self.accounts:
            self.selected_phone = next(iter(self.accounts), None)

        if self.selected_phone:
            account = self.accounts[self.selected_phone]
            self.account_var.set(f"{account.name}  |  {account.phone}")
            self.balance_label.config(
                text="GHS ••••••" if self.hide_balance else money(account.balance)
            )
            self.account_name_label.config(text=account.name)
            self.account_phone_label.config(text=f"📱 {account.phone}")

            if account.account_type == "Merchant":
                self.type_badge.config(text="MERCHANT • 1% FEE", bg="#78350F", fg="#FDE68A")
            else:
                self.type_badge.config(text="PERSONAL WALLET", bg="#1E3A8A", fg="#93C5FD")
        else:
            self.account_var.set("")
            self.balance_label.config(text="GHS 0.00")
            self.account_name_label.config(text="No wallet selected")
            self.account_phone_label.config(text="")
            self.type_badge.config(text="NO ACCOUNT", bg="#334155", fg="#CBD5E1")

        self.stat_accounts.config(text=str(len(self.accounts)))
        self.stat_transactions.config(text=str(len(self.transactions)))
        volume = sum(
            (Decimal(str(t.get("amount", "0"))) for t in self.transactions if isinstance(t, dict)),
            Decimal("0"),
        )
        self.stat_volume.config(text=money(volume))
        self.refresh_history()

    def refresh_history(self):
        if not hasattr(self, "tree"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip().lower()
        shown = 0

        for idx, tx in enumerate(reversed(self.transactions)):
            if not isinstance(tx, dict):
                continue
            searchable = " ".join(
                str(tx.get(k, "")) for k in ("date", "type", "sender", "receiver", "note")
            ).lower()
            if query and query not in searchable:
                continue

            tx_type = tx.get("type", "")
            base_tag = tx_type.lower() if tx_type.lower() in ("deposit", "transfer", "withdrawal") else "deposit"
            tag = f"{base_tag}_alt" if idx % 2 == 1 else base_tag

            self.tree.insert(
                "",
                "end",
                values=(
                    tx.get("date", ""),
                    tx_type.upper(),
                    tx.get("sender", "") or "—",
                    tx.get("receiver", "") or "—",
                    money(tx.get("amount", 0)),
                    money(tx.get("fee", 0)),
                ),
                tags=(tag,),
            )
            shown += 1

        total = len(self.transactions)
        if query:
            self.filter_count_label.config(text=f"Showing {shown} matching result(s) out of {total}")
        else:
            self.filter_count_label.config(text=f"Showing {shown} recorded transaction(s)")

    def on_account_selected(self, _event=None):
        selected = self.account_var.get()
        for phone, account in self.accounts.items():
            if selected == f"{account.name}  |  {phone}":
                self.selected_phone = phone
                break
        self.refresh_all()

    def current_account(self):
        if not self.selected_phone or self.selected_phone not in self.accounts:
            messagebox.showerror("No account", "Register or select an account first.")
            return None
        return self.accounts[self.selected_phone]

    def create_account_window(self):
        win = tk.Toplevel(self.root)
        win.title("Register MoMo Wallet")
        win.geometry("500x670")
        win.minsize(440, 520)
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()

        # Dark Modal Header
        hdr = tk.Frame(win, bg=SIDEBAR_BG, height=76)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="Create New MoMo Wallet", bg=SIDEBAR_BG, fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=24, pady=(14, 2))
        tk.Label(
            hdr, text="Register a Personal or Merchant account with PIN security",
            bg=SIDEBAR_BG, fg="#94A3B8", font=("Segoe UI", 9)
        ).pack(anchor="w", padx=24)

        # Scrollable Form Area
        container = tk.Frame(win, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=(12, 8))
        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg=BG)
        form_window = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        form.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(form_window, width=e.width))

        def wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", wheel)

        def close_window():
            canvas.unbind_all("<MouseWheel>")
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", close_window)

        fields = {}

        def add_field(label, key, show=None):
            tk.Label(
                form, text=label, bg=BG, fg=TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(10, 4))
            entry = tk.Entry(
                form, font=("Segoe UI", 10), bg="white", fg=NAVY,
                relief="solid", bd=1, show=show
            )
            entry.pack(fill="x", ipady=8)
            fields[key] = entry

        add_field("Full Name / Business Name", "name")
        add_field("Mobile Number (10 digits, e.g. 0241234567)", "phone")
        add_field("4-Digit Security PIN", "pin", show="•")
        add_field("Confirm 4-Digit PIN", "confirm", show="•")

        tk.Label(
            form, text="Account Type", bg=BG, fg=TEXT,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(12, 4))
        type_var = tk.StringVar(value="Personal")
        type_combo = ttk.Combobox(
            form, textvariable=type_var,
            values=["Personal", "Merchant"], state="readonly", style="Modern.TCombobox"
        )
        type_combo.pack(fill="x")

        add_field("Opening Balance (GHS)", "balance")

        def save_account():
            name = fields["name"].get().strip()
            phone = fields["phone"].get().strip()
            pin = fields["pin"].get().strip()
            confirm = fields["confirm"].get().strip()
            opening_text = fields["balance"].get().strip() or "0"
            try:
                opening = Decimal(opening_text)
                if not opening.is_finite() or opening < 0:
                    raise InvalidOperation
                opening = opening.quantize(Decimal("0.01"))
            except (InvalidOperation, ValueError):
                messagebox.showerror("Invalid balance", "Enter a valid zero or positive opening balance.", parent=win)
                return
            if not name:
                messagebox.showerror("Missing name", "Enter the account holder's name.", parent=win)
                return
            if not valid_phone(phone):
                messagebox.showerror("Invalid phone", "Enter a valid 10-digit Ghana mobile number beginning with 0.", parent=win)
                return
            if phone in self.accounts:
                messagebox.showerror("Account exists", "An account is already registered with this number.", parent=win)
                return
            if len(pin) != 4 or not pin.isdigit():
                messagebox.showerror("Invalid PIN", "Your PIN must contain exactly 4 digits.", parent=win)
                return
            if pin != confirm:
                messagebox.showerror("PIN mismatch", "The PINs do not match.", parent=win)
                return

            cls = MerchantAccount if type_var.get() == "Merchant" else PersonalAccount
            account = cls(name, phone, opening, pin_hash(pin))
            self.accounts[phone] = account
            self.selected_phone = phone
            self.save_data()
            self.refresh_all()
            close_window()
            messagebox.showinfo("Account created", f"{name}'s wallet has been registered successfully.")

        buttons = tk.Frame(win, bg=BG)
        buttons.pack(fill="x", padx=20, pady=(6, 18))

        cancel_btn = tk.Button(
            buttons, text="CANCEL", command=close_window,
            bg="#E2E8F0", fg=TEXT, relief="flat", padx=20, pady=11,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        cancel_btn.pack(side="left")

        create_btn = tk.Button(
            buttons, text="CREATE WALLET", command=save_account,
            bg=GREEN, fg="white", activebackground=GREEN_DARK,
            activeforeground="white", relief="flat", padx=24, pady=11,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        create_btn.pack(side="right")
        self.add_hover(create_btn, GREEN, GREEN_DARK)

    def ask_pin(self, account, title="Confirm transaction"):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("360x235")
        dialog.resizable(False, False)
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()

        hdr = tk.Frame(dialog, bg=SIDEBAR_BG, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="🔒  PIN Authorization Required", bg=SIDEBAR_BG, fg="white",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=16)

        tk.Label(
            dialog, text=f"Enter 4-digit PIN for {account.name}", bg=BG, fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(18, 10))

        entry = tk.Entry(
            dialog, show="●", font=("Segoe UI", 16, "bold"),
            justify="center", bg="white", fg=NAVY, relief="solid", bd=1
        )
        entry.pack(padx=55, fill="x", ipady=7)
        entry.focus_set()
        result = {"ok": False}

        def confirm():
            try:
                if not account.verify_pin(entry.get().strip()):
                    raise InvalidPinError("The PIN you entered is incorrect.")
                result["ok"] = True
                dialog.destroy()
            except InvalidPinError as exc:
                messagebox.showerror("Incorrect PIN", str(exc), parent=dialog)
                entry.delete(0, "end")

        btn = tk.Button(
            dialog, text="AUTHORIZE", command=confirm, bg=GREEN, fg="white",
            relief="flat", font=("Segoe UI", 9, "bold"), padx=28, pady=10, cursor="hand2"
        )
        btn.pack(pady=16)
        self.add_hover(btn, GREEN, GREEN_DARK)
        dialog.bind("<Return>", lambda _e: confirm())
        self.root.wait_window(dialog)
        return result["ok"]

    def transaction_dialog(self, title, subtitle, accent_color, fields, submit_text, callback):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("450x440")
        win.resizable(False, False)
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()

        hdr = tk.Frame(win, bg=SIDEBAR_BG, height=74)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text=title, bg=SIDEBAR_BG, fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=24, pady=(14, 2))
        tk.Label(
            hdr, text=subtitle, bg=SIDEBAR_BG, fg="#94A3B8",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=24)

        entries = {}
        for key, label in fields:
            tk.Label(
                win, text=label, bg=BG, fg=TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=24, pady=(14, 4))
            entry = tk.Entry(
                win, font=("Segoe UI", 11), bg="white", fg=NAVY,
                relief="solid", bd=1
            )
            entry.pack(fill="x", padx=24, ipady=8)
            entries[key] = entry

        if fields:
            entries[fields[0][0]].focus_set()

        def submit():
            if callback(entries, win):
                win.destroy()

        btn = tk.Button(
            win, text=submit_text, command=submit, bg=accent_color, fg="white",
            activebackground=accent_color, activeforeground="white",
            relief="flat", font=("Segoe UI", 10, "bold"),
            padx=20, pady=12, cursor="hand2"
        )
        btn.pack(fill="x", padx=24, pady=24)
        win.bind("<Return>", lambda _e: submit())
        return win

    def deposit_window(self):
        account = self.current_account()
        if not account:
            return

        def submit(entries, win):
            try:
                amount = to_amount(entries["amount"].get())
                account.deposit(amount)
                tx = Transaction("Deposit", amount, receiver=account.phone, note="Cash deposit")
                self.transactions.append(tx.to_dict())
                self.save_data()
                self.refresh_all()
                messagebox.showinfo(
                    "Deposit successful",
                    f"{money(amount)} deposited into {account.name}'s wallet.",
                    parent=self.root,
                )
                return True
            except MoMoError as exc:
                messagebox.showerror("Deposit failed", str(exc), parent=win)
                return False

        self.transaction_dialog(
            "Deposit Money",
            f"Add funds to {account.name} ({account.phone})",
            GREEN,
            [("amount", "Amount to Deposit (GHS)")],
            "CONFIRM DEPOSIT",
            submit,
        )

    def withdraw_window(self):
        account = self.current_account()
        if not account:
            return

        def submit(entries, win):
            try:
                amount = to_amount(entries["amount"].get())
                if amount > account.balance:
                    raise InsufficientFundsError("Your wallet balance is too low.")
                if not self.ask_pin(account, "Authorize withdrawal"):
                    return False
                account.withdraw(amount)
                self.transactions.append(Transaction("Withdrawal", amount, sender=account.phone).to_dict())
                self.save_data()
                self.refresh_all()
                messagebox.showinfo("Withdrawal successful", f"{money(amount)} withdrawn.", parent=self.root)
                return True
            except MoMoError as exc:
                messagebox.showerror("Withdrawal failed", str(exc), parent=win)
                return False

        self.transaction_dialog(
            "Withdraw Money",
            f"Available balance: {money(account.balance)}",
            BLUE,
            [("amount", "Amount to Withdraw (GHS)")],
            "PROCEED TO PIN",
            submit,
        )

    def transfer_window(self):
        sender = self.current_account()
        if not sender:
            return

        fee_note = "Merchant account: 1% fee applies" if sender.account_type == "Merchant" else "Personal account: Zero transfer fee"

        def submit(entries, win):
            try:
                receiver_phone = entries["phone"].get().strip()
                if receiver_phone not in self.accounts:
                    raise AccountNotFoundError("Transfers are allowed only to registered wallet accounts.")
                if receiver_phone == sender.phone:
                    raise MoMoError("You cannot transfer money to your own account.")

                amount = to_amount(entries["amount"].get())
                receiver = self.accounts[receiver_phone]
                fee = sender.transaction_fee(amount)
                total = amount + fee
                if total > sender.balance:
                    raise InsufficientFundsError(f"You need {money(total)} including the fee.")
                if not self.ask_pin(sender, "Authorize transfer"):
                    return False

                sender.withdraw(total)
                receiver.deposit(amount)
                tx = Transaction(
                    "Transfer", amount, sender=sender.phone,
                    receiver=receiver.phone, fee=fee
                )
                self.transactions.append(tx.to_dict())
                self.save_data()
                self.refresh_all()
                messagebox.showinfo(
                    "Transfer successful",
                    f"{money(amount)} sent to {receiver.name}.\nFee: {money(fee)}",
                    parent=self.root,
                )
                return True
            except MoMoError as exc:
                messagebox.showerror("Transfer failed", str(exc), parent=win)
                return False

        self.transaction_dialog(
            "Transfer Money",
            f"From {sender.name} • {fee_note}",
            PURPLE,
            [
                ("phone", "Recipient's Registered Mobile Number"),
                ("amount", "Transfer Amount (GHS)"),
            ],
            "PROCEED TO PIN",
            submit,
        )

    def export_statement(self):
        account = self.current_account()
        if not account:
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save wallet statement",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"statement_{account.phone}.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Type", "Sender", "Receiver", "Amount (GHS)", "Fee (GHS)", "Note"])
                for tx in self.transactions:
                    if isinstance(tx, dict) and account.phone in (tx.get("sender"), tx.get("receiver")):
                        writer.writerow([
                            tx.get("date"),
                            tx.get("type"),
                            tx.get("sender"),
                            tx.get("receiver"),
                            tx.get("amount"),
                            tx.get("fee"),
                            tx.get("note", ""),
                        ])
            messagebox.showinfo("Export complete", f"Statement saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export error", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    app = MoMoApp(root)
    root.mainloop()