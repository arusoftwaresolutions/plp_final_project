"""
Payment integration module with mock implementation and real integration scaffolding
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import stripe
from config import settings

class PaymentProcessor:
    """Base payment processor interface"""
    
    def create_payment_intent(self, amount: float, currency: str = "usd") -> Dict[str, Any]:
        raise NotImplementedError
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        raise NotImplementedError

class MockPaymentProcessor(PaymentProcessor):
    """Mock payment processor for development and testing"""
    
    def create_payment_intent(self, amount: float, currency: str = "usd") -> Dict[str, Any]:
        return {
            "id": f"pi_mock_{hash(str(amount))}",
            "amount": int(amount * 100),  # Convert to cents
            "currency": currency,
            "status": "requires_payment_method",
            "client_secret": f"pi_mock_{hash(str(amount))}_secret"
        }
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        if not payment_intent_id.startswith("pi_mock_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mock payment intent ID"
            )
        
        return {
            "id": payment_intent_id,
            "status": "succeeded",
            "amount_received": 1000,  # Mock amount
            "currency": "usd"
        }
    
    def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        if not payment_intent_id.startswith("pi_mock_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mock payment intent ID"
            )
        
        return {
            "id": f"re_mock_{hash(payment_intent_id)}",
            "payment_intent": payment_intent_id,
            "amount": int((amount or 1000) * 100),
            "status": "succeeded"
        }

class StripePaymentProcessor(PaymentProcessor):
    """Real Stripe payment processor"""
    
    def __init__(self):
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        stripe.api_key = settings.stripe_secret_key
    
    def create_payment_intent(self, amount: float, currency: str = "usd") -> Dict[str, Any]:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                "id": intent.id,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status,
                "client_secret": intent.client_secret
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount_received": intent.amount_received,
                "currency": intent.currency
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
    
    def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int((amount or 0) * 100) if amount else None
            )
            return {
                "id": refund.id,
                "payment_intent": refund.payment_intent,
                "amount": refund.amount,
                "status": refund.status
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

def get_payment_processor() -> PaymentProcessor:
    """Get the appropriate payment processor based on configuration"""
    if settings.stripe_secret_key:
        return StripePaymentProcessor()
    else:
        return MockPaymentProcessor()

# Payment service functions
def create_donation_payment(amount: float, campaign_id: str, donor_email: str) -> Dict[str, Any]:
    """Create a payment intent for a donation"""
    processor = get_payment_processor()
    
    payment_intent = processor.create_payment_intent(amount)
    
    # In a real implementation, you would store the payment intent in the database
    # with metadata about the campaign and donor
    
    return {
        "payment_intent": payment_intent,
        "campaign_id": campaign_id,
        "donor_email": donor_email,
        "amount": amount
    }

def process_donation_payment(payment_intent_id: str) -> Dict[str, Any]:
    """Process a completed donation payment"""
    processor = get_payment_processor()
    
    result = processor.confirm_payment(payment_intent_id)
    
    if result["status"] == "succeeded":
        # In a real implementation, you would:
        # 1. Update the campaign's current_amount
        # 2. Create a donation record
        # 3. Send confirmation emails
        pass
    
    return result

def refund_donation(payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
    """Refund a donation"""
    processor = get_payment_processor()
    
    result = processor.refund_payment(payment_intent_id, amount)
    
    if result["status"] == "succeeded":
        # In a real implementation, you would:
        # 1. Update the campaign's current_amount
        # 2. Create a refund record
        # 3. Send notification emails
        pass
    
    return result
