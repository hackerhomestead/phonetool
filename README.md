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

## Usage

```bash
# List all contacts (with options to filter and limit)
python3 list_contacts.py
python3 list_contacts.py --search phonetool_test   # filter by search term
python3 list_contacts.py --account Molly            # filter by account name
python3 list_contacts.py --fields name,phone        # choose fields to display
python3 list_contacts.py --limit 10                 # limit results

# Add 5 test contacts
python3 add_contacts.py

# Delete test contacts
python3 delete_contacts.py
```

## Tools

- **list_contacts.py**: List contacts with filtering options (`--account`, `--search`, `--fields`, `--limit`)
- **add_contacts.py**: Creates 5 test contacts (Alice, Bob, Charlie, Diana, Eve) with name, phone, email, and company data
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
