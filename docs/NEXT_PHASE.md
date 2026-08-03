# NEXT_PHASE.md — FinanceFlow

## Remaining Client Requirements (from original project brief, still open)
- Contact page with English/Telugu language switcher (localStorage-based, per original spec)
- Advanced animations pass (original brief listed this as a distinct later phase — partially satisfied incidentally by Phase 1 auth animations and Phase 2-4 hover/count-up work, but never done as a dedicated pass)
- Final QA phase across the whole app
- Migration: SQLite (local) → Supabase PostgreSQL (production)
- Deployment: Render → Vercel
- Cash flow reporting (mentioned in original brief, never scoped in detail, never built)
- Mobile device QA (real devices, not just CSS breakpoints)

## Immediate Housekeeping (before new features)
1. **Confirm the Phase 2.5 fix landed** — verify the 3 Excel URL patterns are actually in the live `urls.py`, `openpyxl` is installed and in `requirements.txt`, and re-test import/export end-to-end.
2. **Audit `password_reset_email.html` / `password_reset_subject.txt`** — these are referenced by `CustomPasswordResetView` but were never created. Password reset may currently be broken at the email-send step. Ask the client to confirm, or request `forms.py`/current `urls.py` to check.
3. **Get `forms.py`** — `CustomUserCreationForm` has never been shown to Claude; signup's real field set/validation is unaudited.

## Priority Order (suggested)
1. Housekeeping items above (low effort, closes real risk)
2. Reconcile auth-page design technique with dashboard/group_detail (client may not have noticed the inconsistency yet — worth flagging before building more pages on either pattern)
3. Build shared `base.html` + one shared `design-system.css` + `shared-utilities.js` *now*, before the Contact page and any further pages get built on the old copy-paste-per-file pattern — every page added without this makes the eventual consolidation more expensive
4. Contact page + Telugu/English switcher
5. Mobile device QA pass
6. Cash flow reporting (needs scoping conversation with client first — brief only mentions it in passing)
7. Supabase + Vercel migration (deployment-only, no UI work, do last so app is feature-complete first)

## Features Intentionally Postponed
- Payment history in Excel export/import (client hasn't asked for it yet; flagged as a limitation, not a requested feature)
- Real Google OAuth on login (button currently a placeholder; client hasn't asked to complete it)
- Weekly (vs current daily) payment cadence toggle — client said "in future we are doing weekly," not now
- Performance optimization of `total_paid`/`balance` aggregation — not a problem at current data volume
- `search_borrowers` AJAX endpoint wiring into group_detail's search box (currently client-side filter only; endpoint exists unused)

## Notes for Whoever Picks This Up
- Read `PROJECT_CONTEXT.md`'s "Known inconsistency" note before touching auth pages or dashboard — they use different background techniques on purpose (organic result of iteration, not a deliberate design decision), and unifying them is a real task, not a typo fix.
- Don't assume `base.html` exists. It doesn't. Every template is standalone.
- Client has been consistently strict about: inspect before coding, don't rewrite what isn't asked for, confirm before touching money calculations. Keep that pattern.
