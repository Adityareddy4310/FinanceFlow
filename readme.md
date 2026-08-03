```markdown
<p align="center">
  <img src="docs/images/logo.png" alt="FinanceFlow Logo" width="72" />
</p>

<h1 align="center">FinanceFlow</h1>

<p align="center">
  <strong>Enterprise finance collection management for small-scale lenders</strong>
</p>

<p align="center">
  Digitize daily loan collections, borrower ledgers, cash flow, and Excel workflows<br>
  with a modern Django-powered dashboard.
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#demo">Demo</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#tech-stack">Tech Stack</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/UI-Custom%20Fintech-B8863B?style=flat-square" alt="UI" />
</p>

---

## Overview

FinanceFlow is a production-oriented Django application built for small finance businesses that still run collections on notebooks or Excel sheets.

It helps teams:

- Manage multiple **finance groups** with isolated ledgers  
- Track **daily repayments** and outstanding balances  
- Record **cash flow** (collections, loans given, expenses)  
- Import / export borrower data via **Excel**  
- Work from a clean, modern dashboard designed for daily use  

Built from scratch with Django + Vanilla JavaScript and a custom fintech-inspired design system.

---

## Demo

> Replace with your actual demo link

**Live demo** :  



## Features

### Authentication
- User registration & secure login  
- Password reset via email  
- Session-based authentication  

### Finance Groups
- Create and manage multiple collection groups  
- Separate borrower ledgers per group  
- Independent statistics and cash flow  

### Borrower & Loan Management
- Add, edit, and delete borrowers  
- Search by name or serial number  
- Daily repayment tracking with automatic balance calculation  
- “Give New Loan” without creating duplicate borrowers  
- Paid borrower highlighting  
- Historical payment preservation  

### Cash Flow
- Daily collections, loans given, and interest  
- Expense categories (Petrol, Food, Rent, Salaries, Misc)  
- Automatic net cash & running cash  
- Monthly reconciliation  

### Excel Workflows
- **Import**: bulk upload with preview, validation, and duplicate handling  
- **Export**: complete ledger download  

### Dashboard & UX
- Real-time group stats (borrowers, outstanding, totals)  
- Enterprise-style UI (dark cinematic theme + cream surfaces)  
- Fully responsive (desktop → mobile)  
- English + Telugu language support  

### Contact
- Professional contact page with form validation and email delivery  

---

## Screenshots

| Dashboard | Group Ledger |
|-----------|--------------|
| ![Dashboard](docs\images\Dashboard.png) | ![Group Ledger](docs\images\finance-group1.png) |

| Cash Flow | Excel Import |
|-----------|--------------|
| ![Cash Flow](docs\images\cash-flow.png) | ![Import](docs\images\excel-import.png) |

| Login | Contact |
|-------|---------|
| ![Login](docs\images\login.png) | ![Contact](docs\images\contact.png) |

| Mobile |
|--------|
| ![Mobile](docs\images\mobile.jpeg) |

---

## Tech Stack

| Layer            | Technology                          |
|------------------|-------------------------------------|
| Backend          | Python 3.11+, Django 4.2            |
| Frontend         | HTML5, CSS3, Vanilla JavaScript     |
| Database         | SQLite (dev) · PostgreSQL planned   |
| Excel            | openpyxl                            |
| Auth             | Django Authentication               |
| Email            | Gmail SMTP                          |
| Icons / Fonts    | Lucide · Inter · Space Grotesk      |
| Design           | Custom fintech design system        |

---

## Project Structure

```text
financeapp/
├── accounts/          # Authentication & user management
├── finance/           # Core business logic (groups, borrowers, cashflow)
├── templates/         # Django templates
├── static/            # CSS, JS, images
├── media/             # Uploaded files
├── docs/
│   └── images/        # README screenshots
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Adityareddy4310/financeapp.git
cd financeapp
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

> **Note:** Configure email settings in `settings.py` for password reset and contact form delivery.

---

## Roadmap

- [ ] PostgreSQL / Supabase migration  
- [ ] Role-based access control (Admin / Collector / Viewer)  
- [ ] REST API  
- [ ] Docker support  
- [ ] Audit logs  
- [ ] Charts & analytics  
- [ ] WhatsApp / SMS reminders  
- [ ] Payment gateway integration  
- [ ] Progressive Web App (PWA)  

---

## Author

**Aditya Reddy**

- GitHub: [Adityareddy4310](https://github.com/Adityareddy4310)  
- LinkedIn: [Add your LinkedIn URL]  

---


<p align="center">
  Built for real finance teams · Designed for daily use
</p>
```

