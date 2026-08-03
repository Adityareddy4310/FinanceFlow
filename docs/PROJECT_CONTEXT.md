# PROJECT_CONTEXT.md — FinanceFlow

## Project Overview
Django loan-collection management SaaS for small-scale financiers. Tracks borrower ledgers, daily payment collections, outstanding balances per Finance Group. Owner: Aditya. Design language: enterprise fintech (Stripe/Linear/Revolut-inspired), charcoal + ivory + gold palette.

## Tech Stack
- Backend: Django 4.2.7, SQLite (dev), Supabase Postgres (planned, not started)
- Frontend: Vanilla JS (no framework, no bundler), plain CSS (no Tailwind), self-contained per-template `<style>` blocks
- Fonts: Google Fonts — Inter (body/UI), Space Grotesk (headings)
- Icons: Lucide via `<script src="https://unpkg.com/lucide@latest">` + `lucide.createIcons()` — **no emoji icons**, replaced in Phase 3
- Excel: `openpyxl` (added this project; not yet confirmed in `requirements.txt`)
- Hosting: currently Render; planned move to Vercel + Supabase (unstarted)

## Folder Structure (known)
```
core/
  templates/
    registration/
      login.html
      signup.html
      password_reset.html
      password_reset_done.html
      password_reset_confirm.html
      password_reset_complete.html
    core/
      dashboard.html
      group_detail.html
  views.py
  models.py
  forms.py        (not inspected — CustomUserCreationForm lives here, never shown to Claude)
  urls.py         (not inspected directly — only known via error traceback + our own added lines)
requirements.txt  (not inspected — openpyxl needs adding, unconfirmed)
```
**Note:** Original plan called for `base.html`, `design-system.css`, shared navbar/footer, `shared-utilities.js` (Phase 0). This was never actually built — every template ended up fully self-contained instead (own `<style>`, own font links, own Lucide script tag, own JS). Treat this as the current reality, not the old plan.

## Database Models (`models.py` — confirmed, verbatim)
```python
class FinanceGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    day = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Borrower(models.Model):
    finance_group = models.ForeignKey(FinanceGroup, related_name='borrowers')
    serial_number = models.IntegerField()
    name = models.CharField(max_length=100, blank=True, default='')
    amount_given = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_of_loan = models.DateField(null=True, blank=True)
    # unique_together: (finance_group, serial_number)
    # @property total_paid = amount_paid + sum(all weekly_payments, NOT month-scoped)
    # @property balance = amount_given - total_paid

class WeeklyPayment(models.Model):
    borrower = models.ForeignKey(Borrower, related_name='weekly_payments')
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # unique_together: (borrower, payment_date)
```
**Important:** model is named `WeeklyPayment` but is currently used for **daily** payments (client confirmed: daily now, weekly cadence possibly later). Do not assume weekly-only semantics.

## All API Endpoints
| Path | View | Method | Notes |
|---|---|---|---|
| `/` | `home` | GET | redirect to dashboard/login |
| `/login/` | Django auth | GET/POST | |
| `/logout/` | Django auth | GET | |
| `/signup/` | `signup` | GET/POST | uses `CustomUserCreationForm` |
| `/password-reset/` | `CustomPasswordResetView` | GET/POST | |
| `/password-reset/done/` | `password_reset_done` | GET | |
| `/password-reset/<uidb64>/<token>/` | `CustomPasswordResetConfirmView` | GET/POST | |
| `/password-reset/complete/` | `password_reset_complete` | GET | |
| `/dashboard/` | `dashboard` | GET | auto-seeds 2 default groups if user has none |
| `/group/<int:group_id>/` | `group_detail` | GET | supports `?search=` |
| `/api/group/<id>/edit/` | `edit_finance_group` | POST | |
| `/api/group/<id>/search/` | `search_borrowers` | GET | AJAX, `?q=` |
| `/api/group/<id>/add-borrower/` | `add_borrower` | POST | |
| `/api/borrower/<id>/delete/` | `delete_borrower` | POST | |
| `/api/borrower/<id>/update-payment/` | `update_payment` | POST | |
| `/api/borrower/<id>/update-amount-paid/` | `update_amount_paid` | POST | |
| `/api/borrower/<id>/update/` | `update_borrower` | POST | |
| `/api/group/<id>/import-excel/preview/` | `import_borrowers_preview` | POST | **added this project — confirm present in live `urls.py`** |
| `/api/group/<id>/import-excel/confirm/` | `import_borrowers_confirm` | POST | same caveat |
| `/api/group/<id>/export-excel/` | `export_borrowers_excel` | GET | same caveat |

The 3 Excel routes were given to the user as a snippet to paste into `urls.py`; a 404 was hit once before they were added. **Verify these 3 lines are actually live before assuming the feature works.**

## Authentication Flow
Django built-in auth + `CustomUserCreationForm` (email/phone signup, file not inspected by Claude). Password reset uses custom views (`CustomPasswordResetView`, `CustomPasswordResetConfirmView`) pointing at custom templates and `email_template_name='registration/password_reset_email.html'` + `subject_template_name='registration/password_reset_subject.txt'` — **these two files were never created in this conversation.** Password reset emails will likely fail to render until they exist.

## Dashboard Implementation
`core/dashboard.html`. Self-contained (own nav, no shared base.html). Palette: charcoal bg (`#15130F`), ivory group cards (`#FAF3E7`), gold accent. 3 gradient stat cards (indigo/emerald/gold-plum) with client-side count-up computed from rendered group data. Group cards: name, day, location, borrower count, balance, edit modal (PATCHes via `edit_finance_group`), full-card link to `group_detail`. Auto-seeds "Vizag Finance" / "Eluru Finance" on first visit if user has zero groups (backend behavior, in `views.py`).

## Finance Group (Workspace) Implementation
`core/group_detail.html`. Current version = Phase 4 (polished). Structure:
- Breadcrumb nav (Dashboard > Group Name) + logout
- Workspace header: icon, group name, schedule (`group.day`) + location (`group.location`) meta row, month pill (`month_name`)
- 4 gradient stat cards: Total Borrowers, Total Loan Amount, Total Collected, Outstanding Balance (all computed client-side from `borrowersData`)
- Search box (client-side filter, not the `/api/group/<id>/search/` AJAX endpoint — that endpoint exists but isn't currently wired into this page's search box; the box filters the already-rendered table via JS)
- Import/Export Excel toolbar
- Borrower table: Sr#, Name, Loan Date, **Loan Amount** (renamed from "Amount" in Phase 4), Paid, Balance, Status badge (Paid/Active, computed client-side from `balance <= 0`), one column per day of the current month, Action (delete icon)
- Add Borrower form (unchanged fields/endpoint since Phase 0)
- Import preview modal + Delete confirm modal (custom, replaces native `confirm()`)

## Borrower Implementation
CRUD via inline table-cell editing (click cell → input → blur/Enter saves via fetch) for name/date/amount/paid, icon-button + confirm-modal for delete, form at bottom for create. All calls hit the endpoints listed above. `_create_or_update_borrower()` helper in `views.py` is the single source of truth for borrower creation/update — used by both manual add and Excel import so behavior is identical between the two paths.

## Payment Implementation
One `WeeklyPayment` row per `(borrower, payment_date)` per day of the currently-viewed month. Editing a payment cell calls `update_payment` (POST, `{date, amount}`), uses `get_or_create`. Cells are visually distinct: green tint + bold for `amount > 0`, muted "—" for empty (Phase 4). `total_paid`/`balance` sum **all** `WeeklyPayment` rows ever, not month-scoped — this is why carry-forward across months already works with zero schema changes (confirmed via `models.py` audit).

## Excel Import Implementation
Two-step, no direct DB write on upload:
1. `import_borrowers_preview` — parses `.xlsx`/`.xls` via `openpyxl`, validates every row (missing/invalid serial, name, date, amount; duplicate serial within file; duplicate vs existing DB serials), returns JSON preview. **Writes nothing.**
2. Browser shows preview modal (valid rows green, errors red, duplicates flagged), user picks "Skip duplicates" or "Replace existing" from a dropdown, clicks Confirm.
3. `import_borrowers_confirm` — receives the previewed rows back (not the file again), wraps in `transaction.atomic()`, calls `_create_or_update_borrower()` per row (same helper as manual add), returns created/updated/skipped counts.

Expected columns (in order, row 1 = header): Serial Number, Borrower Name, Loan Date, Loan Amount.

## Excel Export Implementation
`export_borrowers_excel` — GET, streams a real `.xlsx` built with `openpyxl`. Columns: Serial Number, Borrower Name, Loan Date, Loan Amount, Amount Paid, Outstanding Balance, Status. First 4 columns match import format exactly (round-trip compatible). **Known limitation: payment history (day-by-day) is NOT exported or re-importable** — only loan basics.

## Cash Flow Implementation
**Not implemented.** Mentioned in the original project brief ("cash flow across finance groups") but no cash-flow-specific view, endpoint, or template exists yet.

## Mobile Compatibility
Responsive breakpoints at 1100px / 900px / 640px on both `dashboard.html` and `group_detail.html`: stat cards go 4→2→1 columns, add-form collapses, search box goes full-width, table remains horizontally scrollable (sticky left columns preserved) rather than reflowing. **Not yet tested on real devices** — only via CSS breakpoints.

## UI Architecture / Current Enterprise Design Language
Locked palette (dashboard + group_detail):
```
--bg: #15130F        (charcoal page background)
--box: #FAF3E7        (ivory panel/card surface)
--box-alt: #F1E8D8    (secondary ivory surface)
--accent: #B8863B     (gold)
--accent-hover: #8C6529
--glow: #D9A857        (lighter gold)
--text-on-dark: #EDE6D8
--text-on-light: #241F1B
--forest: #2F5233 (success/paid)
--rust: #A63D40 (error/delete)
--indigo-1/2, --emerald-1/2, --plum-2: used only for stat-card gradients
```
Fonts: Space Grotesk (headings/numbers), Inter (body/UI). Background technique: dot-grid + 3 blurred blob shapes (CSS, animated drift).

**Known inconsistency:** the auth pages (login/signup/password-reset) use a *different* background technique — an animated `<canvas>` particle field + split-screen showcase layout — built in an earlier phase before the dot-grid/blob system was established for dashboard/group_detail. Both share the same charcoal/ivory/gold color values, but the visual technique differs. Not yet reconciled. Auth pages went through 3 palette iterations before landing here (navy/purple glass → serif "ledger" ink/paper concept → indigo/emerald-then-gold on navy → current charcoal/ivory/gold) — only the last is current.

## Existing JavaScript Architecture
No framework, no modules, no build step. Each template has one inline `<script>` block. Common patterns repeated in every page:
- `getCookie('csrftoken')` — manual cookie parsing for CSRF token (no `{% csrf_token %}` form field used for API calls; a hidden `{% csrf_token %}` tag is dropped in the page and/or the cookie is read directly)
- All mutations: `fetch(url, {method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken':...}, body: JSON.stringify(...)})`
- Success path: `location.reload()` (full page reload after almost every mutation — no SPA-style state patching except the Dashboard's group-edit modal, which patches the DOM directly instead of reloading)
- `lucide.createIcons()` called on `window.load` and again after any `innerHTML` rewrite that injects new `data-lucide` elements (e.g. after `renderTable()`)
- Count-up number animation: shared `runCountUp(el, target)` pattern (easeOutCubic, ~900ms), duplicated per-file, not extracted to a shared script

## Existing CSS Architecture
No shared stylesheet. Every template redeclares the same `:root` CSS variables independently. Palette is kept consistent **by convention only** — there is no single source of truth. A future palette change requires editing every template file individually.

## Important Implementation Decisions
- `total_paid`/`balance` are lifetime aggregates (sum of ALL `WeeklyPayment` rows, no month filter) — this is *why* monthly carry-forward already works correctly with zero migrations; confirmed by inspecting `models.py` directly rather than assuming.
- `_create_or_update_borrower()` extracted as a shared helper specifically so manual-add and Excel-import produce byte-identical borrower/payment records — no behavioral fork between the two entry points.
- Excel import is preview-then-confirm (two HTTP round trips) rather than validate-and-commit-in-one-request, so invalid files never touch the DB and the user sees exactly what will happen before it happens.
- Import/export column order intentionally kept symmetric (first 4 columns) for backup/restore round-tripping, even though export has 3 extra reference-only columns.

## Constraints (as given by client across the conversation)
- `settings.py`: never modify.
- `models.py`: do not modify unless explicitly authorized for a specific feature (was authorized once, for the Excel feature's supporting helper function — **no schema/migration was actually needed**, so no model changes exist yet).
- `views.py` / `urls.py`: originally off-limits, later explicitly reopened for new features only ("don't rewrite existing CRUD, do reuse it"). Existing view functions must remain behaviorally identical unless a bug is confirmed.
- Default work surface: templates, CSS, JS.
- Never change business logic/calculations unless explicitly requested and confirmed.

## Coding Conventions
- ₹ currency: formatted client-side via `.toLocaleString('en-IN')`, ₹ symbol prepended in template strings or via CSS `::before { content: '₹' }` on `.money` classes.
- Icons: Lucide only, `data-lucide="name"` attributes, never emoji-as-icon.
- Class naming: plain descriptive kebab-case (`.stat-card`, `.btn-toolbar`, `.icon-btn`), no BEM strictness, no utility-class framework.
- Every new interactive element gets a loading state (`.loading` class + CSS spinner via `::after`) for any button that fires a fetch call.
