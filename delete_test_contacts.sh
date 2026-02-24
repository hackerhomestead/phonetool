#!/bin/bash
# Delete test contacts added by add_test_contacts.sh

if ! adb devices | grep -q "device$" 2>/dev/null; then
  echo "Error: No device connected. Connect device and enable USB debugging."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Backing up contacts before deletion..."
"$SCRIPT_DIR/backup_contacts.sh"

if [ $? -ne 0 ]; then
  echo "Backup failed, aborting..."
  exit 1
fi

echo "Finding test contacts..."

RAW_DATA=$(adb shell 'content query --uri content://com.android.contacts/raw_contacts' | grep 'account_name=test_contact_')

if [ -z "$RAW_DATA" ]; then
  echo "No test contacts found."
  exit 0
fi

DELETE_COUNT=0

for line in $RAW_DATA; do
  RAW_ID=$(echo "$line" | sed -n 's/.*_id=//p' | sed 's/,.*//')
  
  if [ -n "$RAW_ID" ]; then
    adb shell 'content delete --uri content://com.android.contacts/data --where "raw_contact_id='$RAW_ID'"' > /dev/null 2>&1
    adb shell 'content delete --uri content://com.android.contacts/raw_contacts --where "_id='$RAW_ID'"' > /dev/null 2>&1
    echo "Deleted contact ID: $RAW_ID"
    DELETE_COUNT=$((DELETE_COUNT + 1))
  fi
done

echo ""
echo "Done! Deleted $DELETE_COUNT test contact(s)."
echo "Backup saved to: contacts_backup_*.vcf"
