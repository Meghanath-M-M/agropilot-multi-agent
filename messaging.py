"""
AgroPilot Messaging Module
Handles WhatsApp message delivery via Twilio with graceful simulation fallback.
"""

import logging
from typing import Dict, Tuple

import config

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
except ImportError:
    Client = None
    logger.info("Twilio package not installed. Messaging will be simulated.")


class WhatsAppMessenger:
    """Sends formatted advisory messages via Twilio WhatsApp API.

    Falls back to simulated sending if Twilio credentials are missing
    or the twilio package is not installed.
    """

    def __init__(self) -> None:
        self.account_sid: str = config.TWILIO_ACCOUNT_SID
        self.auth_token: str = config.TWILIO_AUTH_TOKEN
        self.from_number: str = config.TWILIO_WHATSAPP_NUMBER

        self.is_configured: bool = bool(
            Client is not None
            and self.account_sid
            and self.auth_token
            and self.account_sid != "your_twilio_account_sid_here"
        )

        if self.is_configured:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Twilio client init failed: {e}")
                self.is_configured = False
        else:
            logger.info("WhatsApp messaging running in demo mode.")

    def format_message(self, advisory: Dict) -> str:
        """Formats advisory data into a structured WhatsApp message.

        Args:
            advisory: Complete advisory dictionary from the orchestrator.

        Returns:
            Formatted multi-line string with emojis and bilingual content.
        """
        crop = advisory.get("crop", {})
        weather = advisory.get("weather", {})
        pest = advisory.get("pest", {})
        market = advisory.get("market", {})

        lines = [
            f"🌾 *AgroPilot Advisory / कृषि सलाह* 🌾",
            f"📍 *Location:* {advisory.get('farmer_location')}",
            f"📅 {advisory.get('timestamp', 'Today')}",
            "",
            f"🌦️ *Weather / मौसम:*",
            f"   {weather.get('temp')}°C | Humidity {weather.get('humidity')}%",
            f"   {weather.get('condition', '').capitalize()}",
            "",
            f"🌱 *Crop / फसल:* {crop.get('crop_name')}",
            f"   💡 {crop.get('reason', '')[:120]}",
            f"   🕐 Sow: {crop.get('sowing_time')} | Harvest: {crop.get('harvest_time')}",
            "",
        ]

        # Add pest alert only if medium/high severity
        if pest.get("severity") in ("medium", "high"):
            lines.extend([
                f"🐛 *Pest Alert / कीट चेतावनी:*",
                f"   ⚠️ {pest.get('pest_name')} ({pest.get('severity').upper()} risk)",
                f"   🌿 Organic: {pest.get('organic_treatment', '')[:100]}",
                f"   ⏰ Action by: {pest.get('action_by_date')}",
                "",
            ])

        lines.extend([
            f"💰 *Market / बाज़ार:*",
            f"   ₹{market.get('price')}/{market.get('unit')} ({market.get('trend')})",
            f"   🏪 Best: {market.get('best_market')}",
            f"   📈 {market.get('sell_timing', '')[:80]}",
            "",
            f"📈 *Expected Income:* ₹{advisory.get('expected_income', 0):,}/acre",
            f"   (Previous: ₹{advisory.get('previous_income', 0):,} → {advisory.get('income_improvement')})",
            "",
            f"📞 *For expert help, reply to this message.*",
            f"✅ _Verified by AgroPilot AI Expert System_",
        ])

        return "\n".join(lines)

    def send_message(self, to_number: str, advisory: Dict) -> Tuple[bool, str]:
        """Send the formatted advisory via WhatsApp.

        Args:
            to_number: Farmer's phone number (with country code).
            advisory: Complete advisory dictionary.

        Returns:
            Tuple of (success: bool, status_message: str).
        """
        formatted_message = self.format_message(advisory)

        # Normalize WhatsApp prefix for recipient
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        # Normalize WhatsApp prefix for sender
        from_num = self.from_number
        if from_num and not from_num.startswith("whatsapp:"):
            from_num = f"whatsapp:{from_num}"

        if not self.is_configured:
            logger.info(f"SIMULATED WhatsApp → {to_number}:\n{formatted_message}")
            return True, "WhatsApp advisory delivered to farmer successfully! (Demo Mode)"

        try:
            message = self.client.messages.create(
                from_=from_num,
                body=formatted_message,
                to=to_number
            )
            logger.info(f"WhatsApp sent: {message.sid}")
            return True, f"✅ WhatsApp advisory delivered! Message ID: {message.sid}"
        except Exception as e:
            error_str = str(e)
            logger.error(f"Twilio send failed: {error_str}")

            # Provide helpful error messages
            if "not a valid WhatsApp" in error_str or "21608" in error_str:
                hint = ("The recipient must first join the Twilio Sandbox. "
                        "Ask them to send 'join <your-code>' to the sandbox number on WhatsApp.")
            elif "21211" in error_str or "invalid" in error_str.lower():
                hint = "Check the phone number format — it should be like +919876543210."
            elif "20003" in error_str or "authenticate" in error_str.lower():
                hint = "Twilio credentials may be incorrect. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env."
            else:
                hint = f"Twilio error: {error_str[:120]}"

            return False, f"⚠️ WhatsApp delivery failed — {hint}"

