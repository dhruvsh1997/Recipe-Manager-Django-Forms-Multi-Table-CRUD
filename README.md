# 🍳 Recipe Manager — Django Forms + Multi-Table CRUD

A Django web app for managing recipes and their ingredients, built around **Django Forms**, **ModelForms**, and **inline formsets** for editing related records on one page. Demonstrates clean form-driven CRUD across two related tables (`Recipe` ↔ `Ingredient`), plus a soft-delete + 24-hour recovery window.

Scheduling for the hard-delete cleanups uses **[django-crontab](https://pypi.org/project/django-crontab/)** so cron entries live inside `settings.py` and are managed via Django commands instead of editing the OS crontab directly.

---

## ✨ Features

- Add, list, search, edit, and delete recipes (multi-table)
- Edit a recipe and its ingredients on one page (inline formsets)
- Field-level + cross-field validation via Django Forms
- Soft delete with 24-hour grace period (Trash bin)
- Restore + permanent (hard) delete
- Automated daily cleanup of expired soft-deleted records via **django-crontab**
- Warm, light-themed UI — inline CSS, no build step

---

## 🧱 Tech Stack

- Python 3.10+
- Django 4.x or 5.x
- django-crontab (scheduler)
- SQLite (default)

---

## 📁 Project Structure

```
recipe_project/
├── recipe_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── kitchen/
│   ├── management/
│   │   └── commands/
│   │       └── cleanup_deleted.py
│   ├── migrations/
│   ├── templates/
│   │   └── kitchen/
│   │       ├── recipe_list.html
│   │       ├── recipe_form.html
│   │       ├── recipe_confirm_delete.html
│   │       ├── recipe_confirm_hard_delete.html
│   │       └── trash_list.html
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
└── manage.py
```

---

## 🚀 Setup

```bash
# 1. Clone and enter
git clone <your-repo-url>
cd recipe_project

# 2. Virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django django-crontab

# 4. Migrate
python manage.py makemigrations
python manage.py migrate

# 5. Run the server
python manage.py runserver
```

Open <http://localhost:8000/>.

---

## 🗺 Routes

| Method | URL                          | Purpose                              |
|--------|------------------------------|--------------------------------------|
| GET    | `/`                          | List + search recipes                |
| GET/POST | `/add/`                    | Add new recipe + ingredients         |
| GET/POST | `/<id>/edit/`              | Edit recipe + ingredients (formset)  |
| GET/POST | `/<id>/delete/`            | Soft delete                          |
| GET    | `/trash/`                    | Trash bin                            |
| GET    | `/<id>/restore/`             | Restore                              |
| GET/POST | `/<id>/hard-delete/`       | Permanently delete                   |

---

## 🧾 Forms in This Project

- **`RecipeForm`** (`ModelForm`) — edits the parent record, with custom `clean_prep_minutes` validation.
- **`IngredientFormSet`** — created with `inlineformset_factory(Recipe, Ingredient, ...)`. Renders multiple ingredient rows tied to one recipe; supports add and delete on the same page.
- **`RecipeSearchForm`** (plain `Form`) — search box, not tied to any model.

The save flow uses `transaction.atomic()` so the parent recipe and its child ingredients commit together or not at all.

---

## 🗑 Soft Delete

Same `SoftDeleteModel` abstract pattern used across all three projects:

- `is_deleted` + `deleted_at` fields
- `objects` manager hides deleted rows; `all_objects` shows everything
- `.delete()` soft-deletes by default; `.delete(hard=True)` removes the row
- `.restore()` undoes a soft delete
- `is_recoverable` is `True` while inside the 24h window

---

## ⏰ Scheduling with django-crontab

`django-crontab` is a small library that lets you declare cron jobs **inside `settings.py`** and then sync them to the OS crontab with a Django command. You don't have to know cron syntax intimately — but the schedule strings are still standard 5-field cron expressions.

### Step 1 — Install (already in setup above)

```bash
pip install django-crontab
```

### Step 2 — Add to `INSTALLED_APPS`

In `recipe_project/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_crontab',
    'kitchen',
]
```

### Step 3 — Define the job in `settings.py`

```python
CRONJOBS = [
    # ('cron schedule', 'python.dotted.path.to.callable')
    ('0 3 * * *', 'kitchen.cron.run_cleanup'),
]
```

The schedule `0 3 * * *` means **3:00 AM every day**. Field order is:

```
minute  hour  day-of-month  month  day-of-week
  0       3        *           *         *
```

Other common examples:
- `*/15 * * * *` — every 15 minutes
- `0 */6 * * *` — every 6 hours, on the hour
- `30 2 * * 0` — 2:30 AM every Sunday

### Step 4 — Create the callable

`django-crontab` expects a regular Python function (not a Django management command). Easiest path: write a tiny wrapper that calls your existing `cleanup_deleted` command.

Create `kitchen/cron.py`:

```python
from django.core.management import call_command


def run_cleanup():
    """Entry point for django-crontab — runs the cleanup_deleted command."""
    call_command('cleanup_deleted')
```

This way the same logic stays runnable both as `python manage.py cleanup_deleted` (manual) and via the scheduler.

### Step 5 — Register the jobs with the OS crontab

`django-crontab` doesn't run a daemon — it writes your `CRONJOBS` entries into the actual OS crontab. After defining them, you have to **add** them:

```bash
python manage.py crontab add
```

You should see something like:

```
adding cronjob: (abc123hash) -> ('0 3 * * *', 'kitchen.cron.run_cleanup')
```

Confirm with the OS:

```bash
crontab -l
```

You'll see a line `django-crontab` added, prefixed with the hash so it can manage it later.

### Step 6 — Other useful commands

```bash
python manage.py crontab show     # list jobs django-crontab is managing
python manage.py crontab remove   # remove all jobs it added
python manage.py crontab add      # re-add (run this after changing settings.CRONJOBS)
```

**Important:** every time you change `CRONJOBS` in `settings.py`, you must run `crontab remove` then `crontab add` (or `crontab add` again — it deduplicates by hash). The OS crontab is not auto-synced.

### Step 7 — Logging the output

By default, django-crontab discards stdout/stderr. To capture logs, add this to `settings.py`:

```python
CRONTAB_COMMAND_PREFIX = ''  # optional: env vars / activation if needed
CRONJOBS = [
    ('0 3 * * *', 'kitchen.cron.run_cleanup', '>> /tmp/recipe_cleanup.log 2>&1'),
]
```

The third tuple element is appended to the cron command line. After changing this, re-run `python manage.py crontab remove && python manage.py crontab add`.

### Step 8 — Test it

You can either:

1. **Run the wrapper function directly** in a Django shell:

   ```bash
   python manage.py shell
   >>> from kitchen.cron import run_cleanup
   >>> run_cleanup()
   ```

2. **Fast-forward the schedule** for one round: temporarily change the cron expression to `* * * * *` (every minute) and the recovery window in `models.py` to `timedelta(minutes=2)`, then `crontab remove && crontab add`, soft-delete a recipe, wait, and watch it disappear. Revert both changes afterward.

### Windows users

`django-crontab` only works on Unix-style systems (Linux, macOS, WSL) because it writes to the OS `cron`. On native Windows, use **Task Scheduler** to run `python manage.py cleanup_deleted` directly — see the Library project's README for those steps. Or develop inside WSL2.

---

## 🔁 Why django-crontab here vs Celery?

- This project has only **one** periodic job and **no** background queue.
- django-crontab needs no extra services (no Redis, no worker process).
- The Tasks API project demonstrates Celery Beat for cases where you need real async work too.

Pick the smallest tool that does the job.

---

## 🧠 Concepts Covered

- Django Forms vs ModelForms vs Formsets
- Inline formsets for parent/child relationships
- Cross-field and field-level form validation
- Multi-table CRUD inside a single transaction (`transaction.atomic`)
- Soft / hard delete with 24h recovery
- Scheduled jobs via django-crontab + cron expressions
- Wrapping management commands as callables for schedulers

---

## 📜 License

MIT
