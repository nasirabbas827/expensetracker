# ExpenseTracker-final  

A **Python/Django** web application that lets users record and manage personal expenses while leveraging blockchain‑style immutability for secure transaction logs. The project also includes a modular admin interface, user profiles, and a simple voting system (election‑candidate features) that showcase how blockchain can be integrated into typical Django apps.

---  

## Overview  

- **Purpose** – Provide a clean, extensible expense‑tracking platform with tamper‑proof records.  
- **Scope** – Core expense CRUD, user authentication, profile management, blockchain‑based vote logging, and an admin dashboard.  
- **Structure** – Standard Django project layout with a single app (`myapp`). All business logic lives in `myapp/` (models, forms, views, URLs, admin).  

> **Note** – The repository contains a zip (`ExpenseTracker-finalcodeafterpro.zip`) and a documentation file (`Project File.docx`). The source code itself is the Django project shown below.  

---  

## Features  

| Feature | Description |
|---------|-------------|
| **Expense CRUD** | Create, read, update, and delete expense entries. |
| **User Profiles** | Extended `Profile` model with picture, address, DOB, etc. |
| **Blockchain‑style Logging** | Each expense (or vote) is stored with a hash chain (`blockchain.py`) to guarantee integrity. |
| **Voting / Election Module** | Simple candidate & election models (`0010_blockchaincode_vote.py` migration) demonstrate how blockchain can secure voting data. |
| **Admin Interface** | Full Django admin (`myapp/admin.py`) for managing users, expenses, and blockchain entries. |
| **REST‑ready** | Forms and serializers are ready for API exposure if needed. |
| **Migrations** | 15 incremental migrations covering profile enhancements, candidate handling, and blockchain integration. |

---  

## Tech Stack  

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.9+ |
| **Framework** | Django 4.x |
| **Database** | SQLite (default) – replace with PostgreSQL/MySQL in production |
| **Frontend** | Django templates (Bootstrap optional) |
| **Blockchain** | Custom lightweight chain implementation (`myapp/blockchain.py`) |
| **Version Control** | Git (GitHub) |
| **Documentation** | `Project File.docx` (high‑level design) |

---  

## Installation  

> The steps below assume a **Unix‑like** environment (Linux/macOS). Windows users can adapt the commands accordingly.

1. **Clone the repository**  

   ```bash
   git clone https://github.com/yourusername/ExpenseTracker-final.git
   cd ExpenseTracker-final
   ```

2. **Create a virtual environment**  

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  

   The project does not ship a `requirements.txt` file, but the core dependencies are:

   ```bash
   pip install Django==4.*   # adjust version as needed
   ```

   *(If a `requirements.txt` is added later,