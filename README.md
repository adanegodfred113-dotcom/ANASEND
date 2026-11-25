# ANASEND Wallet — Digital Finance Simulator

A desktop Mobile Money (MoMo) wallet simulator built with Python and Tkinter, demonstrating core Object-Oriented Programming (OOP) principles, secure PIN-based authorization, precise decimal financial calculations, and persistent JSON storage.

**Author:** Adane Godfred Amofah  
**Index Number:** 2526404689  
**Course:** Python Object-Oriented Programming (Lab 3)  
**Institution:** Ghana Communication Technology University (GCTU) Level 200

---

## Features

- **Account Registration & Management:** Register new **Personal** or **Merchant** wallets with 10-digit Ghana mobile number validation (`0XXXXXXXXX`), custom opening balances, and 4-digit PIN setup.
- **Polymorphic Fee Structure:**
  - **Personal Accounts:** `GHS 0.00` fee on transfers.
  - **Merchant Accounts:** `1%` outgoing transfer fee calculated dynamically via method overriding (`transaction_fee()`).
- **PIN-Protected Transactions:** PINs are never stored in plain text—every PIN is hashed using **SHA-256** (`hashlib`) and verified before withdrawals or transfers execute.
- **Financial Precision:** Uses Python's `decimal.Decimal` module instead of `float` to ensure exact currency rounding (`0.01`).
- **Custom Exception Hierarchy:** Cleanly handles domain-specific errors using `MoMoError`, `InsufficientFundsError`, `InvalidPinError`, `AccountNotFoundError`, and `InvalidAmountError`.
- **Live Dashboard & Search:** Displays real-time wallet balances, total registered accounts, transaction count, total volume, and instant search filtering across transaction history.
- **Persistent Storage & CSV Export:** Automatically saves accounts and transactions to `momo_data.json` and lets users export account statements to `.csv`.

---

## OOP Architecture

| Concept | Implementation in `momoapp.py` |
| :--- | :--- |
| **Encapsulation** | Account state (`balance`, `pin_digest`), PIN verification (`verify_pin`), and balance mutations (`deposit`, `withdraw`) are encapsulated within `Account`. |
| **Inheritance** | `PersonalAccount` and `MerchantAccount` inherit core attributes and methods from the base `Account` class. |
| **Polymorphism** | `MerchantAccount` overrides `transaction_fee(amount)` to apply a 1% transfer fee, while `PersonalAccount` inherits the `0.00` base fee behavior. |
| **Custom Exceptions** | `MoMoError` base class with specialized subclasses for invalid amounts, insufficient balances, wrong PINs, and missing recipient accounts. |

---

## Getting Started

### Prerequisites
- Python **3.10+** (uses only Python standard library modules: `tkinter`, `json`, `hashlib`, `decimal`, `csv`, `pathlib`, `datetime`—no external `pip` packages required).

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/momo-wallet-simulator.git](https://github.com/your-username/momo-wallet-simulator.git)
   cd momo-wallet-simulator
