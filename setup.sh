#!/bin/bash
# Setup script - grant required permissions for contact operations
# Run this after each device reboot

echo "Granting contacts permissions..."

adb shell pm grant com.android.providers.contacts android.permission.READ_CONTACTS
adb shell pm grant com.android.providers.contacts android.permission.WRITE_CONTACTS

echo ""
echo "Permissions granted. You can now run other scripts."
echo "Note: Re-run this after each device reboot."
