#!/bin/bash
# Add test/dummy contacts via ADB

if ! adb devices | grep -q "device$" 2>/dev/null; then
  echo "Error: No device connected. Connect device and enable USB debugging."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Backing up existing contacts first..."
"$SCRIPT_DIR/backup_contacts.sh"

if [ $? -ne 0 ]; then
  echo "Backup failed, aborting..."
  exit 1
fi

TEST_CONTACT_TAG="test_contact_$$"

echo "Adding test contacts..."

declare -a NAMES=("Alice Smith" "Bob Johnson" "Charlie Brown" "Diana Prince" "Eve Wilson")
declare -a PHONES=("+1234567890" "+1234567891" "+1234567892" "+1234567893" "+1234567894")
declare -a EMAILS=("alice@test.local" "bob@test.local" "charlie@test.local" "diana@test.local" "eve@test.local")
declare -a COMPANIES=("Test Corp" "Dummy Inc" "Sample Ltd" "Mock Co" "Fake Org")

TOTAL=${#NAMES[@]}
ADDED=0

for i in "${!NAMES[@]}"; do
  NAME="${NAMES[$i]}"
  PHONE="${PHONES[$i]}"
  EMAIL="${EMAILS[$i]}"
  COMPANY="${COMPANIES[$i]}"

  adb shell 'content insert --uri content://com.android.contacts/raw_contacts --bind "account_type:s:Local" --bind "account_name:s:'"$TEST_CONTACT_TAG"'"' > /dev/null 2>&1

  LAST_RAW=$(adb shell 'content query --uri content://com.android.contacts/raw_contacts' | tail -1)
  RAW_ID=$(echo "$LAST_RAW" | sed -n 's/.*_id=//p' | sed 's/,.*//')

  if [ -z "$RAW_ID" ]; then
    echo "Failed to get raw_contact_id for $NAME"
    continue
  fi

  adb shell 'content insert --uri content://com.android.contacts/data --bind "raw_contact_id:i:'"$RAW_ID"'" --bind "data1:s:'"$NAME"'" --bind "mimetype:s:vnd.android.cursor.item/name"' > /dev/null 2>&1

  adb shell 'content insert --uri content://com.android.contacts/data --bind "raw_contact_id:i:'"$RAW_ID"'" --bind "data1:s:'"$PHONE"'" --bind "mimetype:s:vnd.android.cursor.item/phone_v2"' > /dev/null 2>&1

  adb shell 'content insert --uri content://com.android.contacts/data --bind "raw_contact_id:i:'"$RAW_ID"'" --bind "data1:s:'"$EMAIL"'" --bind "mimetype:s:vnd.android.cursor.item/email_v2"' > /dev/null 2>&1

  adb shell 'content insert --uri content://com.android.contacts/data --bind "raw_contact_id:i:'"$RAW_ID"'" --bind "data1:s:'"$COMPANY"'" --bind "mimetype:s:vnd.android.cursor.item/organization"' > /dev/null 2>&1

  echo "Added: $NAME - $PHONE"
  ADDED=$((ADDED + 1))
done

echo ""
echo "Done! Added $ADDED out of $TOTAL test contacts."
echo "Test contacts tagged with account: $TEST_CONTACT_TAG"
