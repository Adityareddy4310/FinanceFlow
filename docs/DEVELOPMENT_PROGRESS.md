# DEVELOPMENT_PROGRESS.md — FinanceFlow

## Completed Phases

### Phase 0 — Foundation (planned, not actually executed as scoped)
Original plan: `base.html`, `design-system.css`, shared navbar/footer, `shared-utilities.js`. **This did not happen.** Development moved directly into per-page self-contained templates instead, starting Phase 1. Treat Phase 0 as skipped/superseded, not completed.

### Phase 1 — Auth Templates
`login.html`, `signup.html`, `password_reset.html`, `password_reset_done.html`, `password_reset_confirm.html`, `password_reset_complete.html`. Went through 3 full design iterations before acceptance:
1. Glassmorphic purple/navy gradient cards (rejected — "generic AI template look")
2. Serif "ledger book" concept — ink/paper palette, stamp motif, cinematic entrance animation (rejected as still not matching client's vision, though technically distinctive)
3. **Accepted final:** particle-canvas background + split showcase/login-box layout, navy→gold→final charcoal/ivory palette (background must NOT be blue-ish, per explicit client instruction), Inter + Space Grotesk fonts, Lucide icons

### Phase 2 — Dashboard
`dashboard.html`. Charcoal/ivory/gold palette, gradient stat cards (indigo/emerald/gold-plum) with count-up, ivory group cards with edit modal. **Frozen by client — do not modify without a bug being confirmed.**

### Phase 2.5 — Excel Import/Export (unplanned insertion)
Client initially asked for a frontend-only workaround (respecting a no-backend-changes rule), then explicitly reopened `views.py`/`urls.py` for this feature only. Delivered:
- `_create_or_update_borrower()` helper (refactor of existing `add_borrower` logic, behavior-preserving)
- `import_borrowers_preview`, `import_borrowers_confirm`, `export_borrowers_excel` views
- 3 new URL patterns (given as a snippet to paste into `urls.py`)
- `openpyxl` added as a dependency (client needs to `pip install` + add to `requirements.txt`)
- Toolbar + preview modal added to `group_detail.html` (still on the old purple-glass theme at this point)

**Bug encountered:** first test hit `404` on export + "Upload failed" on import — root cause was the 3 URL patterns not yet added to the live `urls.py`. Fix given (exact lines + restart instruction). **Not yet confirmed resolved by the client in this conversation.**

### Phase 3 — Enterprise Workspace UI + Carry-Forward Audit
Two parts:
- **Part 1 (UI):** `group_detail.html` rebuilt to match Dashboard's design language (charcoal bg, gradient stat cards, ivory table panel). All existing JS function names/endpoints preserved exactly.
- **Part 2 (carry-forward logic):** Client reported balances not carrying forward month-to-month. Claude required `models.py` before touching anything (money-correctness caution). After inspection: **no bug existed** — `total_paid`/`balance` already sum ALL `WeeklyPayment` rows with no month filter, so carry-forward was already mathematically correct. No migration, no view change. Confirmed with client and closed.

### Phase 4 — Polish Pass
Same `group_detail.html`, refinement only:
- "Amount" column renamed to "Loan Amount" (client-confirmed, label-only change)
- Workspace header redesigned: icon, title, schedule/location meta row, month pill
- Payment cells: green tint for paid days, muted "—" for empty, distinct hover states
- Delete: icon-only button + custom confirm modal (replacing native `confirm()`)
- Edit affordance: pencil icon fades in on hover over editable cells
- Tabular-nums + right-aligned money column headers
- Styled scrollbar on table container
- Bundled UX fix: payment-cell edit now reads a `data-raw-amount` attribute instead of parsing rendered `₹` text (more reliable prefill, no calculation change)

## Files Modified/Created This Project
- `core/templates/registration/login.html` ✅ final
- `core/templates/registration/signup.html` ✅ final
- `core/templates/registration/password_reset.html` ✅ final
- `core/templates/registration/password_reset_done.html` ✅ final
- `core/templates/registration/password_reset_confirm.html` ✅ final
- `core/templates/registration/password_reset_complete.html` ✅ final
- `core/templates/core/dashboard.html` ✅ final, frozen
- `core/templates/core/group_detail.html` ✅ Phase 4 (latest)
- `core/views.py` — refactored + extended (Excel feature)
- `core/urls.py` — 3 lines given as a snippet, **not confirmed applied**
- `requirements.txt` — `openpyxl` needed, **not confirmed added**

## Current Project Status
Frontend: auth flow + dashboard + finance-group workspace are visually complete and internally consistent (dashboard/group_detail share one design system; auth pages share a different-but-palette-matching one — see inconsistency note in `PROJECT_CONTEXT.md`).

Backend: only the Excel feature added real backend code. All original CRUD views (`add_borrower`, `update_payment`, `update_amount_paid`, `update_borrower`, `delete_borrower`, `search_borrowers`, `edit_finance_group`, `dashboard`, `group_detail`) are behaviorally untouched — `add_borrower` was refactored to call a shared helper but produces identical output.

## Current UI Status
Dashboard: frozen, accepted.
Group workspace: Phase 4 complete, accepted pending client's own device/browser testing.
Auth pages: accepted in Phase 1, never revisited since — may look slightly different in *technique* (not color) from the rest of the app.

## Current Backend Status
No migrations exist or are needed — `models.py` is untouched from the client's original file. `views.py` has 3 new view functions + 1 new helper function on top of the original 12 functions/classes. `urls.py` needs 3 additions the client was told to make manually (unverified). `forms.py` was never shown to Claude — `CustomUserCreationForm` is referenced but unaudited.

## Known Bugs
- **Resolved (pending client confirmation):** 404 on Excel export + "Upload failed" on import — caused by missing `urls.py` entries. Fix provided, not yet confirmed live.
- **Unaudited risk:** `password_reset_email.html` and `password_reset_subject.txt` are referenced by `CustomPasswordResetView` but were never created in this conversation. Password reset emails may fail to render/send until these exist. Not yet reported as broken by the client — flagging preemptively.

## Known Limitations
- Excel export/import round-trips loan basics only; day-by-day payment history is not included.
- `total_paid` sums every `WeeklyPayment` row per borrower on every page load — fine at current scale, will need optimization (caching or a denormalized running total) if borrower histories grow into years of daily rows.
- No shared CSS/JS file — every template independently redeclares the same design tokens. A palette change means editing 8 files by hand.
- Auth pages use a canvas-particle background technique; dashboard/group_detail use a CSS dot-grid + blob technique. Same colors, different mechanism — not unified.
- The group-detail page's search box filters client-side over already-rendered data; the separate `search_borrowers` AJAX endpoint exists in the backend but isn't wired into this particular search box.
- "Continue with Google" button on `login.html` is a non-functional placeholder (`alert()` only).
- No Cash Flow reporting view exists despite being mentioned in the original project brief.

## Future Improvements (not yet scheduled)
- Build the originally-planned `base.html` + `design-system.css` + `shared-utilities.js` to eliminate duplication before adding more pages.
- Reconcile auth-page visual technique with dashboard/group_detail.
- Add payment history to Excel export/import.
- Real Google OAuth (or remove the button).
- Performance pass on `total_paid`/`balance` for long-running borrowers.
- Cash flow reporting page (from original brief).
- Contact page with English/Telugu switcher (from original brief, never started).
- SQLite → Supabase Postgres migration; Render → Vercel deployment (from original brief, never started).
