#!/usr/bin/env python3
"""List contacts with various filtering options."""

import argparse
import re
import subprocess
import sys
from typing import Optional


def run_adb_shell(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        "adb shell \"%s\"" % command.replace('"', '\\"'),
        shell=True, capture_output=True, text=True
    )


def check_device() -> bool:
    result = subprocess.run(
        ["adb", "devices"],
        capture_output=True, text=True
    )
    return any("device" in line for line in result.stdout.split("\n")[1:])


def query_raw_contacts(account_name: Optional[str] = None):
    if account_name:
        cmd = f"content query --uri content://com.android.contacts/raw_contacts --where \"account_name='{account_name}' AND deleted=0\""
    else:
        cmd = "content query --uri content://com.android.contacts/raw_contacts --where \"deleted=0\""
    return run_adb_shell(cmd)


def query_contacts():
    return run_adb_shell("content query --uri content://com.android.contacts/contacts")


def parse_raw_contact(line: str) -> Optional[dict]:
    match = re.search(r'_id=(\d+)', line)
    if not match:
        return None
    raw_id = int(match.group(1))
    
    account_match = re.search(r'account_name=([^,]+)', line)
    account = account_match.group(1) if account_match else None
    
    display_match = re.search(r'display_name=([^,]+)', line)
    display = display_match.group(1) if display_match else None
    
    return {"raw_id": raw_id, "account": account, "display": display}


def get_contact_data(raw_id: int) -> dict:
    data = {"raw_id": raw_id, "name": None, "phone": None, "email": None, "company": None}
    
    name_result = run_adb_shell(
        f"content query --uri content://com.android.contacts/data "
        f"--where \"raw_contact_id={raw_id} AND mimetype='vnd.android.cursor.item/name'\" "
        f"--projection data1"
    )
    if name_result.returncode == 0 and name_result.stdout:
        match = re.search(r'data1=(.+)', name_result.stdout)
        if match:
            data["name"] = match.group(1).strip()
    
    phone_result = run_adb_shell(
        f"content query --uri content://com.android.contacts/data "
        f"--where \"raw_contact_id={raw_id} AND mimetype='vnd.android.cursor.item/phone_v2'\" "
        f"--projection data1"
    )
    if phone_result.returncode == 0 and phone_result.stdout:
        match = re.search(r'data1=(.+)', phone_result.stdout)
        if match:
            data["phone"] = match.group(1).strip()
    
    email_result = run_adb_shell(
        f"content query --uri content://com.android.contacts/data "
        f"--where \"raw_contact_id={raw_id} AND mimetype='vnd.android.cursor.item/email_v2'\" "
        f"--projection data1"
    )
    if email_result.returncode == 0 and email_result.stdout:
        match = re.search(r'data1=(.+)', email_result.stdout)
        if match:
            data["email"] = match.group(1).strip()
    
    company_result = run_adb_shell(
        f"content query --uri content://com.android.contacts/data "
        f"--where \"raw_contact_id={raw_id} AND mimetype='vnd.android.cursor.item/organization'\" "
        f"--projection data1"
    )
    if company_result.returncode == 0 and company_result.stdout:
        match = re.search(r'data1=(.+)', company_result.stdout)
        if match:
            data["company"] = match.group(1).strip()
    
    return data


def list_contacts(
    account: Optional[str] = None,
    search: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None
):
    raw_result = query_raw_contacts(account)
    if raw_result.returncode != 0:
        print("Error querying contacts")
        return
    
    contacts = []
    for line in raw_result.stdout.split("\n"):
        contact = parse_raw_contact(line)
        if contact:
            contacts.append(contact)
    
    if search:
        contacts = [c for c in contacts if search.lower() in str(c.get("account", "")).lower() or search.lower() in str(c.get("display", "")).lower()]
    
    if limit:
        contacts = contacts[:limit]
    
    field_list = fields.split(",") if fields else ["name", "phone", "email", "account"]
    
    for contact in contacts:
        data = get_contact_data(contact["raw_id"])
        data["account"] = contact["account"]
        
        row = []
        for field in field_list:
            val = data.get(field, "")
            row.append(str(val) if val else "-")
        
        print(" | ".join(row))
    
    print(f"\nTotal: {len(contacts)} contacts")


def main():
    parser = argparse.ArgumentParser(description="List Android contacts")
    parser.add_argument("--account", help="Filter by account name")
    parser.add_argument("--search", help="Search in account names")
    parser.add_argument("--fields", default="name,phone,email,account", help="Comma-separated fields to display")
    parser.add_argument("--limit", type=int, help="Limit number of results")
    
    args = parser.parse_args()
    
    if not check_device():
        print("Error: No device connected. Enable USB debugging.")
        sys.exit(1)
    
    list_contacts(
        account=args.account,
        search=args.search,
        fields=args.fields,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
