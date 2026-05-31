"""
PayPal integration service for donations, premium subscriptions, and custom itineraries.
Uses PayPal Smart Buttons (JavaScript SDK) embedded via Streamlit components.
"""

import streamlit as st
import json
import os
import hashlib
from datetime import datetime

# ── Configuration ──
# Replace with your actual PayPal Client ID from https://developer.paypal.com/
PAYPAL_CLIENT_ID = "YOUR_PAYPAL_CLIENT_ID"

# Plan pricing (matches premium_manager.py)
PLANS = {
    "basic": {"name": "Basic Plan", "price": 9.99, "yearly": 99.99},
    "pro": {"name": "Pro Plan", "price": 19.99, "yearly": 199.99},
    "premium": {"name": "Premium Plan", "price": 29.99, "yearly": 299.99},
}

DONATION_AMOUNTS = [5, 15, 50]

ITINERARY_BASE_PRICE = 29
ITINERARY_PER_DAY = 5
ITINERARY_PER_CITY = 10


def _generate_order_id(prefix: str = "ORD") -> str:
    """Generate a unique order ID."""
    raw = f"{prefix}_{datetime.now().isoformat()}_{os.urandom(4).hex()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12].upper()


def _paypal_button_html(
    amount: float,
    description: str,
    order_id: str,
    currency: str = "USD",
    button_label: str = "Pay Now",
    plan_id: str = "",
    custom_data: str = ""
) -> str:
    """
    Generate PayPal Smart Button HTML with the hosted Orders API flow.
    The button creates an order via a placeholder client-side call.
    In production, replace the onError/onCancel handlers with server-side
    order creation + capture via PayPal REST API.
    """
    if PAYPAL_CLIENT_ID == "YOUR_PAYPAL_CLIENT_ID":
        # Demo mode: show payment simulation
        return f"""
        <div style="
            border:2px dashed #e2e8f0;
            border-radius:1rem;
            padding:1.5rem;
            text-align:center;
            background:#fafbfc;
            margin:0.5rem 0;
        ">
            <div style="font-size:2rem;margin-bottom:0.5rem;">&#128179;</div>
            <div style="font-size:1.2rem;font-weight:600;color:#1e293b;">{description}</div>
            <div style="font-size:1.5rem;font-weight:700;color:#cc0000;margin:0.5rem 0;">
                ${amount:.2f} {currency}
            </div>
            <div style="background:#e2e8f0;border-radius:2rem;padding:0.6rem 1.5rem;
                        display:inline-block;font-size:0.85rem;color:#64748b;">
                &#128274; PayPal Sandbox Mode
            </div>
            <div style="margin-top:1rem;font-size:0.8rem;color:#94a3b8;">
                Order: {order_id}<br>
                <em>Set PAYPAL_CLIENT_ID in paypal_service.py to go live</em>
            </div>
        </div>
        """

    # Live PayPal Smart Button
    return f"""
    <script src="https://www.paypal.com/sdk/js?client-id={PAYPAL_CLIENT_ID}&currency={currency}"></script>
    <div id="paypal-button-container-{order_id}"></div>
    <script>
        paypal.Buttons({{
            style: {{
                shape: 'pill',
                color: 'gold',
                layout: 'vertical',
                label: 'paypal',
                tagline: false
            }},
            createOrder: function(data, actions) {{
                return actions.order.create({{
                    purchase_units: [{{
                        reference_id: '{order_id}',
                        description: '{description}',
                        custom_id: '{custom_data}',
                        amount: {{
                            currency_code: '{currency}',
                            value: '{amount:.2f}'
                        }}
                    }}]
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    // Payment successful — redirect to thank-you page
                    window.location.href = window.location.href.split('?')[0] +
                        '?paypal_success=' + data.orderID +
                        '&paypal_amount={amount:.2f}' +
                        '&paypal_plan={plan_id}' +
                        '&paypal_custom={custom_data}';
                }});
            }},
            onError: function(err) {{
                console.error('PayPal Error:', err);
                alert('Payment failed. Please try again.');
            }},
            onCancel: function() {{
                alert('Payment cancelled.');
            }}
        }}).render('#paypal-button-container-{order_id}');
    </script>
    """


def handle_paypal_callback():
    """Process PayPal callback parameters from URL."""
    params = st.query_params
    if "paypal_success" in params:
        order_id = params.get("paypal_success")
        amount = float(params.get("paypal_amount", "0"))
        plan_id = params.get("paypal_plan", "")
        custom = params.get("paypal_custom", "")

        # Clear query params
        st.query_params.clear()

        # Log the transaction
        _log_transaction(order_id, amount, plan_id, custom)

        if plan_id and plan_id in PLANS:
            # Premium subscription purchase
            st.session_state["premium_tier"] = plan_id
            from datetime import timedelta
            st.session_state["premium_expiry"] = (datetime.now() + timedelta(days=30)).isoformat()
            st.balloons()
            st.success(f"🎉 **Payment successful!** Upgraded to {PLANS[plan_id]['name']}. "
                       f"Transaction: {order_id}")
        elif plan_id == "itinerary":
            st.balloons()
            st.success(f"🎉 **Payment successful!** Your itinerary request (${amount:.2f}) "
                       f"has been received. We'll email you within 24 hours. "
                       f"Transaction: {order_id}")
        else:
            # Donation
            st.balloons()
            st.success(f"🎉 **Thank you for your support!** "
                       f"Your donation of ${amount:.2f} is greatly appreciated. "
                       f"Transaction: {order_id}")
        return True
    return False


def _log_transaction(order_id: str, amount: float, plan_id: str, custom: str):
    """Log transaction to local file."""
    log_path = "data/paypal_transactions.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    entry = {
        "order_id": order_id,
        "amount": amount,
        "plan_id": plan_id,
        "custom": custom,
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def display_donation_buttons():
    """Display PayPal donation buttons."""
    st.markdown("""
    <h3 style="text-align:center;margin-bottom:0.5rem;">&#9749; Support Our Work</h3>
    <p style="text-align:center;color:#64748b;margin-bottom:1rem;">
        Your support helps us create better travel guides!
    </p>
    """, unsafe_allow_html=True)

    cols = st.columns(len(DONATION_AMOUNTS))
    for idx, amount in enumerate(DONATION_AMOUNTS):
        with cols[idx]:
            labels = {5: "&#9749; Coffee", 15: "&#127829; Pizza", 50: "&#127775; Star"}
            st.markdown(f"<div style='text-align:center;font-size:2rem;'>{labels.get(amount, '')}</div>",
                       unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center;'>${amount}</h4>", unsafe_allow_html=True)
            order_id = _generate_order_id("DON")
            st.markdown(
                _paypal_button_html(
                    amount=float(amount),
                    description=f"Donation ${amount} - China Travel Guide",
                    order_id=order_id,
                    custom_data=f"donation_{amount}",
                    button_label=f"Donate ${amount}"
                ),
                unsafe_allow_html=True
            )


def display_premium_paypal(bundle_key: str, bundle: dict):
    """Display PayPal checkout for premium plans."""
    price = bundle["price_monthly"]
    order_id = _generate_order_id(f"SUB_{bundle_key}")
    st.markdown(
        _paypal_button_html(
            amount=price,
            description=f"{bundle['name']} - Monthly Subscription",
            order_id=order_id,
            plan_id=bundle_key,
            custom_data=f"premium_{bundle_key}_monthly",
            button_label=f"Subscribe ${price}/mo"
        ),
        unsafe_allow_html=True
    )
    # Yearly option
    st.markdown(
        f"<div style='text-align:center;font-size:0.8rem;color:#94a3b8;margin-top:0.3rem;'>"
        f"Annual: <strong>${bundle['price_yearly']}/year</strong> "
        f"(save ${round(price * 12 - bundle['price_yearly'], 2)})</div>",
        unsafe_allow_html=True
    )
    if st.button(f"Pay ${bundle['price_yearly']}/year", key=f"yearly_{bundle_key}",
                 use_container_width=True):
        order_id_y = _generate_order_id(f"SUB_{bundle_key}_Y")
        st.markdown(
            _paypal_button_html(
                amount=bundle["price_yearly"],
                description=f"{bundle['name']} - Annual Subscription",
                order_id=order_id_y,
                plan_id=bundle_key,
                custom_data=f"premium_{bundle_key}_yearly",
                button_label=f"Subscribe ${bundle['price_yearly']}/yr"
            ),
            unsafe_allow_html=True
        )


def display_itinerary_paypal(itinerary_price: float):
    """Display PayPal checkout for custom itinerary."""
    order_id = _generate_order_id("ITN")
    st.markdown(
        _paypal_button_html(
            amount=itinerary_price,
            description=f"Custom Itinerary - China Travel Guide",
            order_id=order_id,
            plan_id="itinerary",
            custom_data=f"itinerary_{itinerary_price}",
            button_label=f"Pay ${itinerary_price:.2f}"
        ),
        unsafe_allow_html=True
    )
