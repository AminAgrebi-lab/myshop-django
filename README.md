# 🛒 My Shop — Django E-Commerce: Building & Extending Online Shops

> A bilingual (English / Spanish) e-commerce platform built with **Django 5.2**,
> developed as part of the **Django 5 By Example Specialization** (Coursera × Packt).
> The project implements the complete shopping lifecycle — catalog, cart, checkout,
> Stripe payments, coupons, and Redis-powered recommendations — with **full
> internationalization**: translated UI, translated URLs, and translated database content.

---

## ✨ Features

### 🏪 Core Shop
- Product catalog with categories, slugs, and translatable model data
- Session-based shopping cart (add / update / remove items)
- Checkout flow creating orders & order items
- **Stripe Checkout** payments with server-side **webhook** confirmation
- Order management via a customized Django admin

### 🎟️ Extensions
- **Coupon system** with percentage discounts applied to the cart total
- **Recommendation engine** — *"People who bought this also bought"* — powered by **Redis** sorted sets
- Asynchronous task support with **Celery**

### 🌐 Internationalization (i18n / l10n)
- 🇧 / 🇪 **Language switcher** in the header (`English | español`)
- **Language-prefixed & translated URLs** via `i18n_patterns`:
  `/en/cart/` ↔ `/es/carrito/`, `/en/orders/create/` ↔ `/es/pedidos/crear/`
- **Translated templates** (`{% translate %}`, `{% blocktranslate %}`) managed through **Rosetta**
- **Translated model data** (product & category names, slugs, descriptions) via **django-parler**
- **Locale-aware formatting** — `$45.50` (EN) vs `$45,50` (ES)
- **Country-specific validation** with `django-localflavor` (`USZipCodeField`)

---

## 🧰 Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python 3.12 · Django 5.2 |
| Payments   | Stripe (Checkout Sessions + Webhooks) |
| i18n       | django-parler · django-rosetta · django-localflavor |
| Async      | Redis · Celery |
| Database   | SQLite (development) |

---

## 📁 Project Structure

```
myshop-django/
├── shop/       # Catalog: Category & Product (TranslatableModel)
├── cart/       # Session-based cart
├── orders/     # Checkout, Order models, localflavor validation
├── payment/    # Stripe Checkout process + webhook handler
├── coupons/    # Coupon models & forms
├── locale/     # en / es translation catalogs (.po / .mo)
└── myshop/     # settings · urls (i18n_patterns) · celery config
```

---

## 🚀 Getting Started

### Prerequisites
Python 3.12+ · Redis server · Stripe test account

### 1. Install
```bash
git clone https://github.com/<YOUR_USERNAME>/myshop-django.git
cd myshop-django
python -m venv env
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate
pip install -r requirements.txt
```

### 2. Configure
Add your Stripe test keys (never commit real keys!):
```bash
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Run
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Separate terminals:
redis-server
celery -A myshop worker -l info
```

Open `http://127.0.0.1:8000/` → you'll be redirected to `/en/` or `/es/`.

---

## 🌐 i18n Workflow (for contributors)

1. Mark strings: `_('...')` in Python · `{% translate %}` in templates · `_('.../')` in URL patterns
2. Extract: `python manage.py makemessages --all --ignore=env --no-obsolete`
3. Translate in the browser: `http://127.0.0.1:8000/rosetta/` (auto-compiles `.mo`)
4. Edit model content bilingually in the admin (English | Spanish tabs)

> ⚠️ The Stripe webhook lives **outside** `i18n_patterns` at `/payment/webhook/`
> on purpose — external services need one stable, language-free URL.

---

## 🧪 Testing Payments

- Card: `4242 4242 4242 4242` (any future expiry, any CVC)
- Postal code: a US ZIP like `10001` (enforced by `USZipCodeField`)

---

## 📸 Screenshots

| English (`/en/`) | Spanish (`/es/`) |
|:---:|:---:|
| *add your screenshot* | *add your screenshot* |

---

## 🗺️ Roadmap

- [ ] Weight-based shipping costs added to the Stripe charge (AI-assisted challenge)
- [ ] REST API with Django REST Framework (Specialization – Course 3)
- [ ] Production deployment (WSGI/ASGI + static/media on a real server)

---

## 👨‍💻 Author

Amin Agrebi

GitHub:

https://github.com/AminAgrebi-lab