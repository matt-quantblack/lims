import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileType, FileName, Disposition, ContentId, Bcc
import base64


def send_email(to_emails, from_email, subject, html_content=None, content=None, attachments=[], bcc=None):

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content,
        plain_text_content=content)

    if bcc is not None:
        message.bcc = Bcc(bcc)

    for data, filename, filetype in attachments:
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType(filetype)
        attachment.file_name = FileName(filename)
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Example Content ID')
        message.add_attachment(attachment)

    try:
        apikey = os.environ.get('SENDGRID_API_KEY')
        sg = SendGridAPIClient(apikey)
        response = sg.send(message)

        if response.status_code == 202:
            return True, None
        else:
            return False, "Failed: status code is {}".format(response.status_code)
    except Exception as e:
        return False, "Failed: {}".format(e)
