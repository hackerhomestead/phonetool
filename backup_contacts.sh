#!/bin/bash
# Backup existing contacts to a vcf file

if ! adb devices | grep -q "device$" 2>/dev/null; then
  echo "Error: No device connected. Connect device and enable USB debugging."
  exit 1
fi

BACKUP_FILE="contacts_backup_$(date +%Y%m%d_%H%M%S).vcf"

echo "Backing up contacts to $BACKUP_FILE..."

RAW_CONTACTS=$(adb shell content query --uri content://com.android.contacts/raw_contacts)

if [ -z "$RAW_CONTACTS" ]; then
  echo "No contacts to backup."
  exit 0
fi

> "$BACKUP_FILE"

COUNT=0

for line in $RAW_CONTACTS; do
  RAW_ID=$(echo "$line" | sed -n 's/.*_id: //p' | sed 's/ .*//')
  
  if [ -z "$RAW_ID" ]; then
    continue
  fi

  NAME=$(adb shell content query --uri "content://com.android.contacts/data" \
    --where "raw_contact_id=$RAW_ID AND mimetype='vnd.android.cursor.item/name'" \
    --projection data1 2>/dev/null | sed -n 's/.*data1: //p')

  PHONE=$(adb shell content query --uri "content://com.android.contacts/data" \
    --where "raw_contact_id=$RAW_ID AND mimetype='vnd.android.cursor.item/phone_v2'" \
    --projection data1 2>/dev/null | sed -n 's/.*data1: //p')

  EMAIL=$(adb shell content query --uri "content://com.android.contacts/data" \
    --where "raw_contact_id=$RAW_ID AND mimetype='vnd.android.cursor.item/email_v2'" \
    --projection data1 2>/dev/null | sed -n 's/.*data1: //p')

  if [ -n "$NAME" ] || [ -n "$PHONE" ]; then
    echo "BEGIN:VCARD" >> "$BACKUP_FILE"
    echo "VERSION:3.0" >> "$BACKUP_FILE"
    if [ -n "$NAME" ]; then
      echo "N:$NAME;;;;" >> "$BACKUP_FILE"
      echo "FN:$NAME" >> "$BACKUP_FILE"
    fi
    if [ -n "$PHONE" ]; then
      echo "TEL:$PHONE" >> "$BACKUP_FILE"
    fi
    if [ -n "$EMAIL" ]; then
      echo "EMAIL:$EMAIL" >> "$BACKUP_FILE"
    fi
    echo "END:VCARD" >> "$BACKUP_FILE"
    COUNT=$((COUNT + 1))
  fi
done

if [ $COUNT -gt 0 ]; then
  echo "Backup complete: $BACKUP_FILE"
  echo "Contacts backed up: $COUNT"
else
  echo "No contacts found to backup."
  rm -f "$BACKUP_FILE"
fi
