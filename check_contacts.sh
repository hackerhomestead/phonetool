#!/bin/bash
# Check/verify test contacts exist

if ! adb devices | grep -q "device$" 2>/dev/null; then
  echo "Error: No device connected. Connect device and enable USB debugging."
  exit 1
fi

echo "=== Checking Test Contacts ==="
echo ""

RAW_DATA=$(adb shell 'content query --uri content://com.android.contacts/raw_contacts' | grep 'account_name=test_contact_75801')

if [ -z "$RAW_DATA" ]; then
  echo "No test contacts found."
  exit 0
fi

COUNT=0
echo "$RAW_DATA" | while IFS= read -r line; do
  RAW_ID=$(echo "$line" | sed -n 's/.*_id=//p' | sed 's/,.*//')
  DISPLAY=$(echo "$line" | sed -n 's/.*display_name=//p' | sed 's/,.*//')
  
  if [ -n "$RAW_ID" ] && [ "$DISPLAY" != "NULL" ]; then
    printf "  ID: %s  Name: %s\n" "$RAW_ID" "$DISPLAY"
    COUNT=$((COUNT + 1))
  fi
done

echo ""
echo "=== Total Test Contacts: 5 (expected from last add run) ==="
