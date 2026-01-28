# Payment gateway skeletons for future implementation


class BasePaymentGateway:
    """Base class for payment gateways"""

    def create_payment(self, amount, currency="INR"):
        raise NotImplementedError

    def verify_payment(self, payment_id):
        raise NotImplementedError

    def refund_payment(self, payment_id, amount):
        raise NotImplementedError
