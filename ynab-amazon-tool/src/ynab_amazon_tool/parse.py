"""Email parser — classifies emails and extracts order/shipment data into Pydantic models.

Classifies each email as one of: order_confirmation, shipment_notification, refund,
digital, whole_foods, fresh, unknown. Joins order_confirmation + shipment_notification
by order ID to produce a unified ShipmentRecord.

Implemented in Session 3.
"""
