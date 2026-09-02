from django import forms


class CouponApplyForm(forms.Form):
    """
    Simple form for customers to submit a coupon code.
    """
    code = forms.CharField()