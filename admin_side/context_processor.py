from order.models import Order,OrderProduct

def revenue_calculator(request):
    revenue = 0
    tax = 0
    total_revenue = 0
    order_items = Order.objects.all()
    for item in order_items:
            if item.status == 'Order Confirmed':
                revenue += item.order_total
        
    total_revenue = revenue + tax
    return dict(revenue=total_revenue)
