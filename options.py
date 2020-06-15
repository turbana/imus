# where to store sent notifications
CACHE_DIR = "cache"

# email credentials
SMTP_HOSTNAME = "smtp.gmail.com"
SMTP_PORT = 465
with open("auth") as f:
    SMTP_USERNAME, SMTP_PASSWORD = f.read().split()


# email to send notifications to
EMAIL_ADDRESS = "turbana@gmail.com"
