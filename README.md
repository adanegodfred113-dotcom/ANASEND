# MoMo Wallet – Python OOP Lab 3

A desktop Mobile Money (MoMo) wallet simulator built with Python and Tkinter. The project demonstrates Object-Oriented Programming (OOP), classes and objects, inheritance, polymorphism, custom exceptions, transaction history, and JSON file storage.

## Features

- Select between multiple demo MoMo accounts.
- Deposit money into an account.
- Withdraw money from an account.
- Send money to another registered account.
- Record deposits, withdrawals, sent and received transactions.
- Apply a **1% fee** to outgoing transactions from merchant accounts.
- Display account balance and transaction history.
- Save account balances and transaction history in `momo_data.json`.
- Reload saved accounts when the application starts.
- Display friendly error messages for invalid amounts, unknown numbers and insufficient funds.

## Technologies

- Python 3.10+
- Tkinter and ttk (GUI)
- JSON (local data persistence)
- `datetime` (transaction timestamps)

All modules used are included with standard Python installations.

## Project structure

```text
MoMoWallet/
├── momo_wallet.py
├── README.md
└── .gitignore
```

`momo_data.json` is created automatically when the application saves its accounts for the first time.

## Requirements

- Python 3.10 or newer
- A Python installation that includes Tkinter

## How to run

1. Download or clone this repository.
2. Open the project folder in PyCharm or a terminal.
3. Run:

   ```bash
   python momo_wallet.py
   ```

4. Choose an account from the drop-down list.
5. Enter an amount and select Deposit, Withdraw or Send.
6. To send money, enter the recipient's registered phone number in the **Send to** field.

On the first run, the app creates three demonstration accounts:

| Account | Phone | Starting balance |
|---|---|---:|
| Ama Mensah (Personal) | 0241112222 | GH₵500.00 |
| Kofi Boateng (Personal) | 0553334444 | GH₵200.00 |
| Auntie Akos Chop Bar (Merchant) | 0205556666 | GH₵1,000.00 |

These are sample accounts for testing, not real mobile money accounts.

## Merchant fee

Personal accounts pay no transaction fee. Merchant accounts pay 1% on outgoing transactions.

Example: a merchant withdraws GH₵200.00.

- Withdrawal amount: GH₵200.00
- Fee (1%): GH₵2.00
- Total deducted: GH₵202.00

The same merchant fee rule applies when a merchant sends money.

## OOP concepts demonstrated

- **Class:** `Account` defines the common structure and behaviour of an account.
- **Object:** `ama` and `kofi` can be separate objects created from `Account`; each has its own balance and transaction history.
- **Constructor:** `__init__()` initializes an object's attributes.
- **`self`:** refers to the current object.
- **Encapsulation:** account data and operations are grouped in classes.
- **Inheritance:** `MerchantAccount` inherits from `Account`.
- **`super()`:** calls the parent class constructor and methods.
- **Method overriding:** `MerchantAccount` overrides `fee_for()`, `account_type()` and `to_dict()`.
- **Polymorphism:** `withdraw()` calls `self.fee_for(amount)`, so the fee depends on the actual account object.
- **Custom exception:** `InsufficientFundsError` represents an insufficient balance.
- **Persistence:** account objects are converted to dictionaries and stored in JSON.

## Testing checklist

- [ ] Deposit a valid amount.
- [ ] Withdraw a valid amount.
- [ ] Send money from Ama to Kofi.
- [ ] Select Kofi and confirm the received transaction.
- [ ] Withdraw GH₵200 from the merchant account and confirm the GH₵2 fee.
- [ ] Try `abc`, zero and a negative amount.
- [ ] Try withdrawing more than the available balance.
- [ ] Try sending to an unknown phone number.
- [ ] Try sending money to the account's own number.
- [ ] Close and reopen the application; confirm balances and history remain saved.

## Important note

This is an educational simulator. It does not connect to MTN MoMo, Telecel Cash, AirtelTigo/AT Money, banks, payment gateways or real customer accounts. Do not enter real financial or personal information.

## Author

**Adane Godfred Amofah**  
Computer Engineering Student  
Ghana Communication Technology University (GCTU)

## Licence

This project was created for educational and learning purposes.
