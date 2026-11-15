# TAB 00 — INITIATIVE BOOTSTRAP

You are initializing a fresh **Product Initiative Workspace** across Processes 01–06 in this repository. Transfer context through files on disk, not chat history.

## Before anything else

1. Verify that `.agents/skills/` exists at repository root.
2. Confirm or obtain two parameters from the user:
   - **Initiative ID**: unique lowercase kebab-case slug (e.g., `my-product-v1`).
   - **Title**: human-readable product name (e.g., `My Product`).
3. Ensure you do not overwrite an ongoing initiative unless the user explicitly requested `--force`.

## Method 1 — Mechanical Bootstrap (Recommended)

Run the deterministic bootstrap script from repository root:

```bash
python test-harness/bootstrap-initiative.py --initiative-id <slug> --title "<title>"
```

The script will:
- Create all 6 process directories (`product/seed/`, `discovery/`, `definition/`, `app-flow/`, `ux-design/`, `design-system/`).
- Initialize Decision Logs and Control Files from their respective canonical templates.
- Initialize the Process 04 Change Request Register (`10_CHANGE_REQUEST_REGISTER.md`) with a valid sequence-0 header and committed initialization event in `00_APP_FLOW_CONTROL.md`.
- Compute all initial cryptographic SHA-256 hashes on disk and record them into the Control files.
- Automatically execute mechanical checkers (`validate-control.py`, `validate-register.py`) to verify that the workspace is fail-closed compliant.

## Method 2 — Manual Scaffolding (If Shell Execution Is Unavailable)

If running in a shell-restricted environment, scaffold files following these exact rules:

1. **Process 01 (Seed):**
   - Copy `templates/03-DECISION-LOG.md` to `product/seed/03_DECISION_LOG.md`.
   - Replace timestamp placeholder with local time (`YYYY-MM-DD HH:mm Asia/Ho_Chi_Minh`).

2. **Process 02 (Product Discovery):**
   - Copy `templates/02-PRODUCT-DISCOVERY/00-DISCOVERY-CONTROL.md` to `product/discovery/00_DISCOVERY_CONTROL.md`.
   - Replace `REPLACE_WITH_UNIQUE_SLUG` with your initiative ID.

3. **Process 03 (Product Definition):**
   - Copy `templates/03-PRODUCT-DEFINITION/06-DECISION-LOG.md` to `product/definition/06_DECISION_LOG.md`.
   - Copy `templates/03-PRODUCT-DEFINITION/00-PRODUCT-DEFINITION-CONTROL.md` to `product/definition/00_PRODUCT_DEFINITION_CONTROL.md`.
   - Replace initiative ID placeholders.

4. **Process 04 (App Flow):**
   - Copy `templates/04-APP-FLOW/10-DECISION-LOG.md` to `product/app-flow/09_DECISION_LOG.md` (Note: template `10-DECISION-LOG.md` maps to working file `09_DECISION_LOG.md`).
   - Create `product/app-flow/10_CHANGE_REQUEST_REGISTER.md` with:
     ```markdown
     # Change Request Register — <Title>

     | Field | Value |
     |---|---|
     | Process | 04 |
     | Initiative ID | <slug> |
     | Register Schema Version | 1 |
     | Last register sequence | 0 |
     ```
   - Copy `templates/04-APP-FLOW/00-APP-FLOW-CONTROL.md` to `product/app-flow/00_APP_FLOW_CONTROL.md`.
   - Bind initiative ID, set `state_seq: 1`, compute SHA-256 of `09_DECISION_LOG.md` for `decision_log.latest_sha256`, compute SHA-256 of the Register header for `change_request_register.last_verified_sha256`, and append the `CHANGE_REQUEST_REGISTER_INITIALIZED` event to `event_log`.

5. **Process 05 (UX Design):**
   - Copy `templates/05-UX-DESIGN/08-DECISION-LOG.md` to `product/ux-design/08_DECISION_LOG.md`.
   - Copy `templates/05-UX-DESIGN/00-UX-CONTROL.md` to `product/ux-design/00_UX_CONTROL.md`.
   - Bind initiative ID and actual SHA-256 of `08_DECISION_LOG.md`.

6. **Process 06 (Design Systems):**
   - Copy `templates/06-DESIGN-SYSTEMS/07-DECISION-LOG.md` to `product/design-system/07_DECISION_LOG.md`.
   - Copy `templates/06-DESIGN-SYSTEMS/00-DS-CONTROL.md` to `product/design-system/00_DS_CONTROL.md`.
   - Bind initiative ID, platform defaults, and actual SHA-256 of `07_DECISION_LOG.md`.

## Verification Pass

Before declaring the workspace initialized, run the mechanical checkers:

```bash
python test-harness/validate-control.py product/app-flow/00_APP_FLOW_CONTROL.md
python test-harness/validate-register.py product/app-flow/10_CHANGE_REQUEST_REGISTER.md --h-init <register_header_sha256>
python test-harness/validate-control.py product/ux-design/00_UX_CONTROL.md
python test-harness/validate-control.py product/design-system/00_DS_CONTROL.md
```

All checkers must report `PASS`.

## What You Must Not Do

- Do not invent SHA-256 hashes. Always compute them from file bytes on disk.
- Do not approve any gate during bootstrap. All gates must remain `PENDING`.
- Do not modify files in `templates/`. Templates are immutable sources.
- Do not write product ideas or assumptions during bootstrap.

## Next Step

The workspace is now clean and verifiable.
Open a fresh conversation and paste `prompts/01-TAB-EXPLORE.md` along with the user's rough idea to start Tab 01.
