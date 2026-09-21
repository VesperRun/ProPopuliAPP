import logging

import resend

from app.config import settings

logger = logging.getLogger("propopuli.mailer")


def send_verification_email(to_email: str, verify_url: str) -> bool:
    subject = "Verify your ProPopuli account"
    html = f"""
    <p>Confirm this email to post and reply on ProPopuli.</p>
    <p><a href="{verify_url}">Verify email</a></p>
    <p>If you did not sign up, ignore this message.</p>
    <p style="color:#666;font-size:12px;">Link expires in 48 hours.</p>
    """

    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set — verification link (dev): %s", verify_url)
        print(f"[ProPopuli] Verify email for {to_email}: {verify_url}")
        return True

    if not settings.resend_from_email:
        logger.error("RESEND_FROM_EMAIL not set")
        return False

    resend.api_key = settings.resend_api_key
    try:
        resend.Emails.send(
            {
                "from": settings.resend_from_email,
                "to": [to_email],
                "subject": subject,
                "html": html,
            }
        )
        return True
    except Exception as exc:
        logger.error("Resend send failed: %s", exc)
        return False
