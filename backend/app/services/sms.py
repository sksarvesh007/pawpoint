"""SMS service using Twilio."""

import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages via Twilio."""

    def _get_twilio_client(self):
        """Create a Twilio REST client from settings."""
        from twilio.rest import Client as TwilioClient

        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise ValueError("Twilio credentials are not configured")
        return TwilioClient(
            settings.twilio_account_sid,
            settings.twilio_auth_token.get_secret_value(),
        )

    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
    ) -> dict:
        """
        Send an SMS message.

        Args:
            to: Recipient phone number
            body: Message body
            from_number: Sender phone number (defaults to Twilio messaging service)

        Returns:
            Dict with sid and status
        """
        client = self._get_twilio_client()

        kwargs: dict = {
            "body": body,
            "to": to,
        }

        if from_number:
            kwargs["from_"] = from_number
        elif settings.twilio_messaging_service_sid:
            kwargs["messaging_service_sid"] = settings.twilio_messaging_service_sid
        else:
            logger.warning(
                "No SMS sender configured (from_number or messaging_service_sid)"
            )
            return {"sid": None, "status": "not_configured"}

        try:
            message = await asyncio.to_thread(client.messages.create, **kwargs)
            logger.info(f"SMS sent to {to}: sid={message.sid}, status={message.status}")
            return {"sid": message.sid, "status": message.status}
        except Exception as e:
            logger.error(f"Failed to send SMS to {to}: {e}")
            return {"sid": None, "status": "failed", "error": str(e)}

    async def send_appointment_confirmation(
        self,
        phone: str,
        clinic_name: str,
        pet_name: str,
        date: str,
        time: str,
        confirmation_code: str,
        custom_template: str | None = None,
    ) -> dict:
        """
        Send an appointment confirmation SMS.

        Args:
            phone: Recipient phone number
            clinic_name: Name of the clinic
            pet_name: Name of the pet
            date: Appointment date (formatted string)
            time: Appointment time (formatted string)
            confirmation_code: Booking confirmation code
            custom_template: Custom message template (optional)

        Returns:
            Dict with sid and status
        """
        if custom_template:
            body = custom_template.format(
                clinic_name=clinic_name,
                pet_name=pet_name,
                date=date,
                time=time,
                confirmation_code=confirmation_code,
            )
        else:
            body = (
                f"{clinic_name}: Your appointment for {pet_name} is confirmed "
                f"for {date} at {time}. Confirmation #: {confirmation_code}. "
                f"Reply CANCEL to cancel."
            )

        return await self.send_sms(phone, body)

    async def send_appointment_reminder(
        self,
        phone: str,
        clinic_name: str,
        pet_name: str,
        date: str,
        time: str,
        hours_until: int,
        custom_template: str | None = None,
    ) -> dict:
        """
        Send an appointment reminder SMS.

        Args:
            phone: Recipient phone number
            clinic_name: Name of the clinic
            pet_name: Name of the pet
            date: Appointment date (formatted string)
            time: Appointment time (formatted string)
            hours_until: Hours until the appointment
            custom_template: Custom message template (optional)

        Returns:
            Dict with sid and status
        """
        if custom_template:
            body = custom_template.format(
                clinic_name=clinic_name,
                pet_name=pet_name,
                date=date,
                time=time,
                hours_until=hours_until,
            )
        else:
            body = (
                f"{clinic_name} Reminder: {pet_name}'s appointment is "
                f"{'tomorrow' if hours_until >= 20 else 'today'} at {time}. "
                f"Please arrive 10 minutes early. "
                f"Reply CANCEL to cancel or call us to reschedule."
            )

        return await self.send_sms(phone, body)
