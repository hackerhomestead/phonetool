#!/usr/bin/env python3
"""Delete test contacts - use contacts view."""

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
    
    # Query contacts VIEW to get raw contact IDs
    result = run_adb_shell("content query --uri content://com.android.contacts/contacts")
    
    raw_ids = set()
    for line in result.stdout.split("\n"):
        if TEST_TAG in line:
            match = re.search(r'name_raw_contact_id=(\d+)', line)
            if match:
                raw_ids.add(int(match.group(1)))
    
    print(f"Found {len(raw_ids)} test contacts: {sorted(raw_ids)}")
    
    if not raw_ids:
        print("No contacts to delete.")
        return
    
    deleted = 0
    for raw_id in raw_ids:
        # Delete data first, then raw contact
        run_adb_shell(f'content delete --uri content://com.android.contacts/data --where "raw_contact_id={raw_id}"')
        result = run_adb_shell(f'content delete --uri content://com.android.contacts/raw_contacts --where "_id={raw_id}"')
        if result.returncode == 0:
            deleted += 1
            print(f"  Deleted raw ID: {raw_id}")
    
    print(f"\nDeleted: {deleted}/{len(raw_ids)}")

if __name__ == "__main__":
    main()
