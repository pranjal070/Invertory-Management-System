from django import template
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import timedelta, datetime

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sum_inventory_value(items):
    """Calculate the total value of all inventory items"""
    total = 0
    for item in items:
        total += item.quantity * item.price
    return total

@register.filter
def low_stock_count(items):
    """Count items with low stock (less than 10)"""
    count = 0
    for item in items:
        quantity = item.get('quantity', 0)  # Safely retrieve 'quantity' from dictionary
        if quantity < 10:
            count += 1
    return count

@register.filter
def recent_activity_count(items):
    """Count items with recent activity (added or changed in the last 7 days)"""
    count = 0
    one_week_ago = timezone.now() - timedelta(days=7)

    for item in items:
        date_added = item.get('date_added')
        last_changed = item.get('last_changed')

        # Handle different date formats
        if isinstance(date_added, str):
            try:
                # Try ISO format first
                date_added = make_aware(datetime.fromisoformat(date_added.replace('Z', '+00:00')))
            except ValueError:
                try:
                    # Try other common formats
                    date_added = make_aware(datetime.strptime(date_added, '%Y-%m-%dT%H:%M:%S.%f'))
                except ValueError:
                    try:
                        date_added = make_aware(datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S'))
                    except ValueError:
                        date_added = None

        if isinstance(last_changed, str) and last_changed:
            try:
                # Try ISO format first
                last_changed = make_aware(datetime.fromisoformat(last_changed.replace('Z', '+00:00')))
            except ValueError:
                try:
                    # Try other common formats
                    last_changed = make_aware(datetime.strptime(last_changed, '%Y-%m-%dT%H:%M:%S.%f'))
                except ValueError:
                    try:
                        last_changed = make_aware(datetime.strptime(last_changed, '%Y-%m-%d %H:%M:%S'))
                    except ValueError:
                        last_changed = None

        if (date_added and date_added >= one_week_ago) or (last_changed and last_changed >= one_week_ago):
            count += 1

    return count

@register.filter
def sum_inventory_value(items):
    """Calculate the total value of all inventory items"""
    total = 0
    for item in items:
        quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        total += quantity * price
    return total
