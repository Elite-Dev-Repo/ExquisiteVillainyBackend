# Pass/utils.py
import uuid
from .models import Pass

def generate_pass_for_payment(payment_obj):
    """
    Creates a Pass record if the payment is successful 
    and a pass doesn't already exist for it.
    """
    if payment_obj.status == 'success' and not hasattr(payment_obj, 'generated_pass'):
        new_pass_code = f"PASS-{uuid.uuid4().hex[:8].upper()}"
        
        return Pass.objects.create(
            email=payment_obj.email,
            pass_code=new_pass_code,
            payment=payment_obj
        )
    return None