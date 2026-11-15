#!/usr/bin/env python3
"""Bootstrap a fresh Product Initiative workspace across Processes 01-06.

Creates directory structure, initializes Control files, Decision logs, and
the Change Request register with verified cryptographic hashes and timestamps.

Usage:
  python test-harness/bootstrap-initiative.py --initiative-id <slug> [--title "<title>"] [--target-dir <path>] [--force] [--dry-run]
"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def get_local_timestamp() -> str:
    tz = timezone(timedelta(hours=7))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M Asia/Ho_Chi_Minh")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_template(rel_path: str) -> str:
    p = REPO / rel_path
    if not p.exists():
        raise SystemExit(f"FAIL  template not found: {rel_path}")
    return p.read_text(encoding="utf-8")


def write_file(dest: pathlib.Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"[dry-run] write {dest} ({len(content.encode('utf-8'))} bytes)")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Product Initiative Workspace")
    parser.add_argument("--initiative-id", default="seed-initiative-01", help="Unique slug for initiative")
    parser.add_argument("--title", default="Product Initiative", help="Human-readable title")
    parser.add_argument("--target-dir", default="product", help="Target product directory relative to repo root")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing")
    args = parser.parse_args()

    init_id = args.initiative_id.strip()
    title = args.title.strip()
    target_root = REPO / args.target_dir
    ts = get_local_timestamp()

    # Pre-flight check: ensure target directory doesn't have existing non-empty artifacts unless --force
    critical_files = [
        target_root / "seed" / "03_DECISION_LOG.md",
        target_root / "discovery" / "00_DISCOVERY_CONTROL.md",
        target_root / "definition" / "00_PRODUCT_DEFINITION_CONTROL.md",
        target_root / "app-flow" / "00_APP_FLOW_CONTROL.md",
        target_root / "ux-design" / "00_UX_CONTROL.md",
        target_root / "design-system" / "00_DS_CONTROL.md",
    ]
    if not args.force and not args.dry_run:
        existing = [f for f in critical_files if f.exists()]
        if existing:
            print("FAIL  target workspace already contains initialized control files:")
            for f in existing:
                print(f"      - {f.relative_to(REPO)}")
            print("      Pass --force to overwrite.")
            return 1

    print(f"--- Bootstrapping initiative '{init_id}' ({title}) ---")
    print(f"Target directory: {target_root.relative_to(REPO)}")
    print(f"Timestamp: {ts}\n")

    # 1. Process 01 — Seed
    p01_dl_template = read_template("templates/03-DECISION-LOG.md")
    p01_dl_text = p01_dl_template.replace("YYYY-MM-DD HH:mm Asia/Ho_Chi_Minh", ts)
    write_file(target_root / "seed" / "03_DECISION_LOG.md", p01_dl_text, args.dry_run)
    print("✓ Initialized Process 01 (Seed) Decision Log")

    # 2. Process 02 — Product Discovery
    p02_ctrl_template = read_template("templates/02-PRODUCT-DISCOVERY/00-DISCOVERY-CONTROL.md")
    p02_ctrl_text = p02_ctrl_template.replace("REPLACE_WITH_UNIQUE_SLUG", init_id)
    p02_ctrl_text = p02_ctrl_text.replace("YYYY-MM-DD HH:mm Asia/Ho_Chi_Minh", ts)
    write_file(target_root / "discovery" / "00_DISCOVERY_CONTROL.md", p02_ctrl_text, args.dry_run)
    print("✓ Initialized Process 02 (Discovery) Control File")

    # 3. Process 03 — Product Definition
    p03_dl_template = read_template("templates/03-PRODUCT-DEFINITION/06-DECISION-LOG.md")
    p03_dl_text = p03_dl_template.replace("REPLACE_WITH_UNIQUE_SLUG", init_id)
    write_file(target_root / "definition" / "06_DECISION_LOG.md", p03_dl_text, args.dry_run)
    p03_ctrl_template = read_template("templates/03-PRODUCT-DEFINITION/00-PRODUCT-DEFINITION-CONTROL.md")
    p03_ctrl_text = p03_ctrl_template.replace("REPLACE_WITH_UNIQUE_SLUG", init_id)
    write_file(target_root / "definition" / "00_PRODUCT_DEFINITION_CONTROL.md", p03_ctrl_text, args.dry_run)
    print("✓ Initialized Process 03 (Definition) Control & Decision Log")

    # 4. Process 04 — App Flow
    # Note: template 10-DECISION-LOG.md initializes working file 09_DECISION_LOG.md
    p04_dl_template = read_template("templates/04-APP-FLOW/10-DECISION-LOG.md")
    p04_dl_text = p04_dl_template.replace("REPLACE_WITH_UNIQUE_SLUG", init_id)
    write_file(target_root / "app-flow" / "09_DECISION_LOG.md", p04_dl_text, args.dry_run)
    p04_dl_sha = sha256_bytes(p04_dl_text.encode("utf-8"))

    # Initial Register header
    reg_header = f"""# Change Request Register — {title}

| Field | Value |
|---|---|
| Process | 04 |
| Initiative ID | {init_id} |
| Register Schema Version | 1 |
| Last register sequence | 0 |
"""
    write_file(target_root / "app-flow" / "10_CHANGE_REQUEST_REGISTER.md", reg_header, args.dry_run)
    reg_header_sha = sha256_bytes(reg_header.encode("utf-8"))

    p04_ctrl_template = read_template("templates/04-APP-FLOW/00-APP-FLOW-CONTROL.md")
    # Patch P04 Control
    p04_ctrl = p04_ctrl_template.replace('initiative_id: "REPLACE_WITH_UNIQUE_SLUG"', f'initiative_id: "{init_id}"')
    p04_ctrl = p04_ctrl.replace("state_seq: 0", "state_seq: 1")
    p04_ctrl = p04_ctrl.replace("created_at_local: null", f'created_at_local: "{ts}"')
    p04_ctrl = p04_ctrl.replace('last_updated_local: "NOT_VERIFIED"', f'last_updated_local: "{ts}"')
    p04_ctrl = p04_ctrl.replace("latest_sha256: null", f'latest_sha256: "{p04_dl_sha}"')
    p04_ctrl = p04_ctrl.replace("last_verified_sha256: null", f'last_verified_sha256: "{reg_header_sha}"')
    p04_ctrl = p04_ctrl.replace("last_event_id: null", 'last_event_id: "INITIALIZATION"')
    
    # Add initial event to event_log
    initial_event_yaml = f"""event_log:
  - event_type: "CHANGE_REQUEST_REGISTER_INITIALIZED"
    state_seq: 1
    timestamp_local: "{ts}"
    exact_user_command: "NOT_APPLICABLE"
    reason: "Register v1 workspace initialization"
    changed_paths:
      - "{args.target_dir}/app-flow/10_CHANGE_REQUEST_REGISTER.md"
    relevant_hashes:
      register_sha256: "{reg_header_sha}"
    initiative_id: "{init_id}"
    path: "{args.target_dir}/app-flow/10_CHANGE_REQUEST_REGISTER.md"
    register_schema_version: 1
    register_seq: 0
    last_event_id: "INITIALIZATION"
    last_verified_sha256: "{reg_header_sha}" """
    p04_ctrl = p04_ctrl.replace("event_log: []", initial_event_yaml)
    write_file(target_root / "app-flow" / "00_APP_FLOW_CONTROL.md", p04_ctrl, args.dry_run)
    print("✓ Initialized Process 04 (App Flow) Control, Decision Log & Register (v1)")

    # 5. Process 05 — UX Design
    p05_dl_template = read_template("templates/05-UX-DESIGN/08-DECISION-LOG.md")
    p05_dl_text = p05_dl_template.replace("REPLACE_WITH_UNIQUE_SLUG", init_id)
    write_file(target_root / "ux-design" / "08_DECISION_LOG.md", p05_dl_text, args.dry_run)
    p05_dl_sha = sha256_bytes(p05_dl_text.encode("utf-8"))

    p05_ctrl_template = read_template("templates/05-UX-DESIGN/00-UX-CONTROL.md")
    p05_ctrl = p05_ctrl_template.replace('initiative_id: "REPLACE_WITH_VERIFIED_INITIATIVE_ID"', f'initiative_id: "{init_id}"')
    p05_ctrl = p05_ctrl.replace("created_at_local: null", f'created_at_local: "{ts}"')
    p05_ctrl = p05_ctrl.replace('last_updated_local: "NOT_VERIFIED"', f'last_updated_local: "{ts}"')
    p05_ctrl = p05_ctrl.replace("latest_sha256: null", f'latest_sha256: "{p05_dl_sha}"')
    write_file(target_root / "ux-design" / "00_UX_CONTROL.md", p05_ctrl, args.dry_run)
    print("✓ Initialized Process 05 (UX Design) Control & Decision Log")

    # 6. Process 06 — Design Systems
    p06_dl_template = read_template("templates/06-DESIGN-SYSTEMS/07-DECISION-LOG.md")
    p06_dl_text = p06_dl_template.replace("REPLACE_WITH_UNIQUE_SLUG", init_id)
    write_file(target_root / "design-system" / "07_DECISION_LOG.md", p06_dl_text, args.dry_run)
    p06_dl_sha = sha256_bytes(p06_dl_text.encode("utf-8"))

    p06_ctrl_template = read_template("templates/06-DESIGN-SYSTEMS/00-DS-CONTROL.md")
    p06_ctrl = p06_ctrl_template.replace('initiative_id: "REPLACE_WITH_VERIFIED_INITIATIVE_ID"', f'initiative_id: "{init_id}"')
    p06_ctrl = p06_ctrl.replace("created_at_local: null", f'created_at_local: "{ts}"')
    p06_ctrl = p06_ctrl.replace('last_updated_local: "NOT_VERIFIED"', f'last_updated_local: "{ts}"')
    p06_ctrl = p06_ctrl.replace("recorded_at_local: null", f'recorded_at_local: "{ts}"')
    p06_ctrl = p06_ctrl.replace("latest_sha256: null", f'latest_sha256: "{p06_dl_sha}"')
    write_file(target_root / "design-system" / "00_DS_CONTROL.md", p06_ctrl, args.dry_run)
    print("✓ Initialized Process 06 (Design Systems) Control & Decision Log")

    if args.dry_run:
        print("\n[dry-run] Bootstrap preview complete.")
        return 0

    # Verification pass with mechanical checkers
    print("\n--- Running mechanical verification on initialized files ---")
    checkers = [
        ("Process 04 Control", [sys.executable, str(REPO / "test-harness" / "validate-control.py"), str(target_root / "app-flow" / "00_APP_FLOW_CONTROL.md")]),
        ("Process 04 Register", [sys.executable, str(REPO / "test-harness" / "validate-register.py"), str(target_root / "app-flow" / "10_CHANGE_REQUEST_REGISTER.md"), "--h-init", reg_header_sha]),
        ("Process 05 Control", [sys.executable, str(REPO / "test-harness" / "validate-control.py"), str(target_root / "ux-design" / "00_UX_CONTROL.md")]),
        ("Process 06 Control", [sys.executable, str(REPO / "test-harness" / "validate-control.py"), str(target_root / "design-system" / "00_DS_CONTROL.md")]),
    ]

    all_ok = True
    for label, cmd in checkers:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            print(f"FAIL  {label}: returncode {res.returncode}")
            print(res.stdout + res.stderr)
            all_ok = False
        else:
            print(f"PASS  {label}")

    if not all_ok:
        print("\nFAIL  Workspace initialized but failed mechanical verification.")
        return 1

    print("\nWorkspace successfully bootstrapped and verified.")
    print("Next step: Start Tab 01 by pasting prompts/01-TAB-EXPLORE.md into a fresh session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
