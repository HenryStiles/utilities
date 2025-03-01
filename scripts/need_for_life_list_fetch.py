#!/usr/bin/env python3

import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

# Gmail IMAP details (usually don't change)
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# Hard-coded label name we want to fetch
LABEL_NAME = "BirdAlert"

def get_plain_text_body(msg):
    """
    Extracts and returns the plain-text body from an email.message.Message object.
    If the message is multipart, returns the first text/plain part.
    Otherwise returns an empty string if not found.
    """
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                payload = part.get_payload(decode=True)
                try:
                    return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                except:
                    return payload.decode("utf-8", errors="replace")
        return ""
    else:
        if msg.get_content_type() == "text/plain":
            payload = msg.get_payload(decode=True)
            try:
                return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
            except:
                return payload.decode("utf-8", errors="replace")
        else:
            return ""

def fetch_birdalert_emails():
    """
    Main function to fetch emails from LABEL_NAME using IMAP.
    Prints From, Subject, and plain-text content.
    """
    EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not EMAIL_ACCOUNT or not EMAIL_PASSWORD:
        print("ERROR: EMAIL_ACCOUNT and/or EMAIL_PASSWORD environment variables not set.")
        return

    try:
        # Connect via SSL
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

        # Select the label/mailbox (read-only mode so we don't mark emails as read)
        status, _ = mail.select(LABEL_NAME, readonly=True)
        if status != "OK":
            print(f"Could not select label '{LABEL_NAME}'. Status: {status}")
            mail.logout()
            return

        # Get today's date and calculate 10 days ago
        date_since = (datetime.utcnow() - timedelta(days=10)).strftime("%d-%b-%Y")

        # Search for messages from the last 10 days
        status, msg_ids_data = mail.search(None, f'SINCE {date_since}')
        if status != "OK":
            print("Failed to search for messages in label.")
            mail.logout()
            return

        # Convert msg_ids_data to a list of message IDs
        msg_ids = msg_ids_data[0].split()

        # If there are no messages, exit gracefully
        if not msg_ids:
            print(f"No recent messages found in '{LABEL_NAME}' from the last 10 days.")
            mail.logout()
            return

        print(f"Total messages in '{LABEL_NAME}' (last 10 days): {len(msg_ids)}")

        # Function to get INTERNALDATE for each message
        def get_internal_date(msg_id):
            status, response = mail.fetch(msg_id, "(INTERNALDATE)")
            if status != "OK":
                return None
            response_str = response[0].decode()
            date_start = response_str.find('"') + 1
            date_end = response_str.rfind('"')
            internal_date_str = response_str[date_start:date_end]
            return (msg_id, datetime.strptime(internal_date_str, "%d-%b-%Y %H:%M:%S %z"))

        # Fetch dates for each message
        emails_with_dates = [get_internal_date(msg_id) for msg_id in msg_ids]
        emails_with_dates = [item for item in emails_with_dates if item is not None]

        # Sort emails by date (newest first)
        emails_with_dates.sort(key=lambda x: x[1], reverse=True)

        # Get up to the latest 10 messages
        latest_emails = emails_with_dates[:10]
        print(f"looking at {len(latest_emails)} emails")
        # Process only the latest 10 messages
        for msg_id, created_at in latest_emails:
            # Fetch the email
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status == "OK":
                raw_email = msg_data[0][1]
                msg_obj = email.message_from_bytes(raw_email)

                # Decode subject
                subject_parts = decode_header(msg_obj.get("Subject"))
                subject = ""
                for part, enc in subject_parts:
                    if isinstance(part, bytes):
                        subject += part.decode(enc if enc else "utf-8")
                    else:
                        subject += part

                from_ = msg_obj.get("From")

                # Get plain text content
                text_content = get_plain_text_body(msg_obj)

                # Print info
                print("\n------------------------------------------------------------")
                print(f"Email {msg_id.decode()} - Created at: {created_at}")
                print(f"From: {from_}")
                print(f"Subject: {subject}")
                print(f"Text Content:\n{text_content}")

        # Close the mailbox and logout
        mail.close()
        mail.logout()

    except imaplib.IMAP4.error as e:
        print("IMAP Authentication/Connection Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

if __name__ == "__main__":
    fetch_birdalert_emails()

