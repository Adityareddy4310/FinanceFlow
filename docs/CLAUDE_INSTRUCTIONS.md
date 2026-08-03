# CLAUDE_INSTRUCTIONS.md — Permanent Rules for FinanceFlow

These rules apply to every future session on this project, regardless of which phase is active.

1. **Always inspect existing code before coding.** Never assume file contents — ask for the actual file (`models.py`, `views.py`, `urls.py`, `forms.py`, templates) if it hasn't been shown yet, especially before touching anything that affects money calculations or authentication.
2. **Never regenerate a complete file unless necessary.** Prefer targeted edits. Full-file regeneration is only justified for large structural/visual rewrites the client explicitly asked for (e.g. a full page redesign).
3. **If a modification is under ~20 lines, provide only the patch** (the changed lines + enough surrounding context to place them), not the full file.
4. **Preserve all existing functionality.** Every CRUD operation, calculation, endpoint, and behavior that currently works must keep working after any change, unless the client explicitly asked to change it.
5. **Never change business logic unless requested.** This especially applies to `total_paid`, `balance`, payment calculations, and anything touching money. When in doubt, ask to see the model/view code first rather than guessing.
6. **Reuse existing endpoints and functions.** Don't create a parallel/duplicate endpoint or helper if one already does the job — extend or call the existing one (see `_create_or_update_borrower()` as the established pattern).
7. **Minimize token usage.** Default to delivering code as files (via the file-creation tool + present_files), not pasted inline in chat, unless the client asks to see it inline.
8. **Avoid unnecessary explanations.** State what changed and why only where it isn't obvious; skip restating things already established in `PROJECT_CONTEXT.md`.
9. **Keep responses concise.**
10. **Maintain enterprise-quality code.** Loading states on every async button, consistent design tokens, no emoji-as-icon (Lucide only), no inline `alert()`-driven UX where a proper modal is warranted.
11. **Preserve responsive design.** Any template touched must keep working at the existing breakpoints (1100px / 900px / 640px) unless the client asks for a breakpoint change.
12. **Preserve mobile compatibility.** Sticky-column tables, stacking forms, and full-width search/toolbar behavior on small screens must not regress.

## Also carry forward from this project's actual working pattern (not just the client's literal list)
- Flag known inconsistencies/limitations honestly rather than silently working around them (e.g. the auth-page vs dashboard background-technique mismatch, the unaudited `forms.py`).
- When a request touches money logic and the relevant model/view code hasn't been seen yet, say so and ask for it before writing anything — do not guess at financial calculations.
- Client has explicitly frozen the Dashboard — do not modify it without a confirmed bug.
- `settings.py` is permanently off-limits.
