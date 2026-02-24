# phonetool

Android contacts testing framework via ADB - works on GrapheneOS/AOSP without Google accounts.

## Requirements

- Android device with USB debugging enabled
- ADB installed on your computer
- Python 3

## Setup

Grant contacts permissions (run after each device reboot):
```bash
adb shell pm grant com.android.providers.contacts android.permission.READ_CONTACTS
adb shell pm grant com.android.providers.contacts android.permission.WRITE_CONTACTS
```

Or run the setup script:
```bash
./setup.sh
```

## Usage

```bash
# Add 5 test contacts
python3 add_contacts.py

# View test contacts
python3 check_contacts.py

# Delete test contacts
python3 delete_contacts.py
```

## What it does

- **add_contacts.py**: Creates 5 test contacts (Alice, Bob, Charlie, Diana, Eve) with name, phone, email, and company data
- **check_contacts.py**: Lists all test contacts currently on the device
- **delete_contacts.py**: Removes all test contacts by tag

The contacts are tagged with "phonetool_test" in the account name, allowing them to be identified and deleted later.

## How it works

Uses Android's `content` command to interact with the ContactsProvider:
- Creates raw contacts in `content://com.android.contacts/raw_contacts`
- Adds data (name, phone, email, organization) to `content://com.android.contacts/data`
- Queries the contacts view to find and delete contacts

No Google account required - contacts are stored locally on device.

## License

MIT
