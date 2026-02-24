#!/usr/bin/env python3
"""Add test contacts - use fixed tag from file."""

import subprocess
import re
import sys
import os
from typing import Optional

def run_adb_shell(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        f"adb shell '{command}'",
        shell=True, capture_output=True, text=True
    )

def check_device() -> bool:
    result = subprocess.run(
        ["adb", "devices"],
        capture_output=True, text=True
    )
    return any("device" in line for line in result.stdout.split("\n")[1:])

def get_last_raw_contact_id() -> Optional[int]:
    result = run_adb_shell("content query --uri content://com.android.contacts/raw_contacts")
    if result.returncode != 0:
        return None
    lines = result.stdout.strip().split("\n")
    if not lines:
        return None
    last_line = lines[-1]
    match = re.search(r'_id=(\d+)', last_line)
    return int(match.group(1)) if match else None

def add_contact(name: str, phone: str, email: str, company: str, tag: str) -> bool:
    result = run_adb_shell(
        f'content insert --uri content://com.android.contacts/raw_contacts '
        f'--bind "account_type:s:Local" --bind "account_name:s:{tag}"'
    )
    if result.returncode != 0:
        return False
    
    raw_id = get_last_raw_contact_id()
    if not raw_id:
        return False
    
    data_types = [
        ("vnd.android.cursor.item/name", name),
        ("vnd.android.cursor.item/phone_v2", phone),
        ("vnd.android.cursor.item/email_v2", email),
        ("vnd.android.cursor.item/organization", company),
    ]
    
    for mimetype, data in data_types:
        run_adb_shell(
            f'content insert --uri content://com.android.contacts/data '
            f'--bind "raw_contact_id:i:{raw_id}" --bind "data1:s:{data}" '
            f'--bind "mimetype:s:{mimetype}"'
        )
    
    return True


if __name__ == "__main__":
    if not check_device():
        print("Error: No device connected. Enable USB debugging.")
        sys.exit(1)
    
    # Use fixed tag - easier for testing
    TEST_TAG = "phonetool_test"
    
    print(f"Using tag: {TEST_TAG}")
    
    test_data = [
        (f"Alice Smith {TEST_TAG}", "+1234567890", "alice@test.local", "Test Corp"),
        (f"Bob Johnson {TEST_TAG}", "+1234567891", "bob@test.local", "Dummy Inc"),
        (f"Charlie Brown {TEST_TAG}", "+1234567892", "charlie@test.local", "Sample Ltd"),
        (f"Diana Prince {TEST_TAG}", "+1234567893", "diana@test.local", "Mock Co"),
        (f"Eve Wilson {TEST_TAG}", "+1234567894", "eve@test.local", "Fake Org"),
    ]
    
    added = 0
    for name, phone, email, company in test_data:
        if add_contact(name, phone, email, company, TEST_TAG):
            print(f"Added: {name} - {phone}")
            added += 1
    
    print(f"\nDone! Added {added} contacts.")
    
    # Save tag to file
    with open("/tmp/phonetool_tag.txt", "w") as f:
        f.write(TEST_TAG)
