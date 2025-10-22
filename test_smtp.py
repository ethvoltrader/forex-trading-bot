import smtplib
from email_config import SENDER_EMAIL, SENDER_PASSWORD

print("🔍 Testing ProtonMail SMTP Connection...\n")
print("=" * 60)

# Try different ProtonMail SMTP servers
servers = [
    ('smtp.protonmail.com', 465),
    ('mail.protonmail.com', 465),
    ('smtp.protonmail.ch', 465),
    ('127.0.0.1', 1025)  # ProtonMail Bridge if installed
]

for server, port in servers:
    try:
        print(f"\n🔌 Trying {server}:{port}...")
        with smtplib.SMTP_SSL(server, port, timeout=10) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            print(f"✅ SUCCESS! {server}:{port} works!")
            break
    except Exception as e:
        print(f"❌ Failed: {e}")

print("\n" + "=" * 60)
