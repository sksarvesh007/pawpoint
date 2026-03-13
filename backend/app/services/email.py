"""Email service using SendGrid HTTP API."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid."""

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> dict:
        """
        Send an email via SendGrid.

        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body
            from_email: Sender email (defaults to settings)
            from_name: Sender name (defaults to settings)

        Returns:
            Dict with status and message_id
        """
        if not settings.sendgrid_api_key:
            logger.warning("SendGrid API key not configured, skipping email")
            return {"status": "not_configured", "message_id": None}

        sender_email = from_email or settings.email_from_address
        sender_name = from_name or settings.email_from_name

        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": sender_email, "name": sender_name},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}],
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.sendgrid_api_key.get_secret_value()}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )

            if response.status_code in (200, 202):
                message_id = response.headers.get("X-Message-Id")
                logger.info(f"Email sent to {to}: message_id={message_id}")
                return {"status": "sent", "message_id": message_id}
            else:
                logger.error(f"SendGrid error {response.status_code}: {response.text}")
                return {
                    "status": "failed",
                    "message_id": None,
                    "error": response.text,
                }

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return {"status": "failed", "message_id": None, "error": str(e)}

    async def send_appointment_confirmation(
        self,
        email: str,
        clinic_name: str,
        clinic_phone: str | None,
        pet_name: str,
        owner_name: str,
        date: str,
        time: str,
        confirmation_code: str,
        reason: str | None = None,
    ) -> dict:
        """Send an appointment confirmation email."""
        subject = f"Appointment Confirmed - {pet_name} at {clinic_name}"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #3DA99F; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{clinic_name}</h1>
                <p style="margin: 5px 0 0; opacity: 0.9;">Appointment Confirmation</p>
            </div>
            <div style="border: 1px solid #e5e7eb; border-top: none; padding: 20px; border-radius: 0 0 8px 8px;">
                <p>Hello {owner_name},</p>
                <p>Your appointment has been confirmed with the following details:</p>
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                    <tr><td style="padding: 8px 0; color: #6b7280;">Patient:</td><td style="padding: 8px 0; font-weight: bold;">{pet_name}</td></tr>
                    <tr><td style="padding: 8px 0; color: #6b7280;">Date:</td><td style="padding: 8px 0; font-weight: bold;">{date}</td></tr>
                    <tr><td style="padding: 8px 0; color: #6b7280;">Time:</td><td style="padding: 8px 0; font-weight: bold;">{time}</td></tr>
                    {"<tr><td style='padding: 8px 0; color: #6b7280;'>Reason:</td><td style='padding: 8px 0;'>" + reason + "</td></tr>" if reason else ""}
                    <tr><td style="padding: 8px 0; color: #6b7280;">Confirmation #:</td><td style="padding: 8px 0; font-weight: bold;">{confirmation_code}</td></tr>
                </table>
                <p style="color: #6b7280; font-size: 14px;">Please arrive 10 minutes early. If you need to cancel or reschedule, please call us{" at " + clinic_phone if clinic_phone else ""}.</p>
                <p style="color: #6b7280; font-size: 12px; margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 15px;">This is an automated message from {clinic_name}.</p>
            </div>
        </div>
        """
        return await self.send_email(email, subject, html_body)

    async def send_appointment_reminder(
        self,
        email: str,
        clinic_name: str,
        clinic_phone: str | None,
        pet_name: str,
        owner_name: str,
        date: str,
        time: str,
        hours_until: int,
    ) -> dict:
        """Send an appointment reminder email."""
        time_label = "tomorrow" if hours_until >= 20 else "today"
        subject = f"Reminder: {pet_name}'s appointment {time_label} at {clinic_name}"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #3DA99F; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{clinic_name}</h1>
                <p style="margin: 5px 0 0; opacity: 0.9;">Appointment Reminder</p>
            </div>
            <div style="border: 1px solid #e5e7eb; border-top: none; padding: 20px; border-radius: 0 0 8px 8px;">
                <p>Hello {owner_name},</p>
                <p>This is a reminder that <strong>{pet_name}</strong> has an appointment {time_label}:</p>
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {time}</p>
                </div>
                <p>Please arrive 10 minutes early.</p>
                <p style="color: #6b7280; font-size: 14px;">Need to cancel or reschedule? Call us{" at " + clinic_phone if clinic_phone else ""}.</p>
                <p style="color: #6b7280; font-size: 12px; margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 15px;">This is an automated message from {clinic_name}.</p>
            </div>
        </div>
        """
        return await self.send_email(email, subject, html_body)
