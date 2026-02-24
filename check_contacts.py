#!/usr/bin/env python3
"""Check test contacts - use contacts view."""

import sys
import os
import re

TAG_FILE = "/tmp/phonetool_tag.txt"
if os.path.exists(TAG_FILE):
    with open(TAG_FILE) as f:
        TEST_TAG = f.read().strip()
else:
    TEST_TAG = None

sys.path.insert(0, os.path.dirname(__file__))
from add_contacts import run_adb_shell, check_device

def main():
    if not check_device():
        print("Error: No device connected.")
        sys.exit(1)
    
    if not TEST_TAG:
        print("No test tag found. Run add_contacts.py first.")
        return
    
    # Query contacts VIEW (not raw_contacts) - this shows aggregated contacts
    result = run_adb_shell("content query --uri content://com.android.contacts/contacts")
    
    contacts = []
    for line in result.stdout.split("\n"):
        if TEST_TAG in line:
            raw_id_match = re.search(r'name_raw_contact_id=(\d+)', line)
            c_id_match = re.search(r'_id=(\d+)', line)
            display_match = re.search(r'display_name=([^,]+)', line)
            if raw_id_match and c_id_match and display_match:
                contacts.append({
                    "id": int(c_id_match.group(1)),
                    "raw_id": int(raw_id_match.group(1)),
                    "display": display_match.group(1)
                })
    
    print(f"=== Test Contacts (tag: {TEST_TAG}) ===")
    for c in contacts:
        print(f"  Contact ID: {c['id']} (raw: {c['raw_id']}) - {c['display']}")
    print(f"\nTotal: {len(contacts)}")

if __name__ == "__main__":
    main()
