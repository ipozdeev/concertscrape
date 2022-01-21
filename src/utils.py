import logging
import logging.handlers
from email.mime.text import MIMEText
import datetime
import base64

from .gmailtools import get_gmail_client


class EMailBulkHandler(logging.handlers.BufferingHandler):
    """Redirect log output to SMTP."""
    def __init__(self, *args, **kwargs):
        super(EMailBulkHandler, self).__init__(*args, **kwargs)

    @staticmethod
    def send_mail(message):
        msg = MIMEText(message)
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        msg['subject'] = f"concertscrape logs {now}"
        msg['from'] = "teil.von.jenerkraft@gmail.com"
        msg["to"] = "igor.posdeev@gmail.com"

        to_send = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}

        client = get_gmail_client()

        client.users().messages().send(userId="me", body=to_send).execute()

    def flush(self) -> None:
        """Pipe all log records as required."""
        if len(self.buffer) > 0:
            s = "\n".join((self.format(record) for record in self.buffer))
            self.send_mail(s)
            self.buffer = []


logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
eh = EMailBulkHandler(capacity=500)

fm = logging.Formatter('%(asctime)s - %(name)s (%(levelname)s) - %(message)s',
                       datefmt="%m/%d %H:%M:%S")
eh.setFormatter(fm)

logger.addHandler(eh)
