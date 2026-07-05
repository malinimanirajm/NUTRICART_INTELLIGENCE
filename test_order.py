"""
test_order.py
"""

from datetime import datetime

from agents.order.models import Order
from agents.order.models import OrderItem
from agents.order.service import OrderService


def main():

    service = OrderService()

    order = Order(

        order_id="O0001",

        customer_id="C0001",

        ordered_at=datetime.now(),

        items=[

            OrderItem(

                product_id="P00151",

                product_name="NatureNest_Dairy_Item_1",

                quantity=2,

            ),

            OrderItem(

                product_id="P00156",

                product_name="FreshFarm_Dairy_Item_6",

                quantity=1,

            ),

        ],

    )

    print("=" * 80)
    print("PLACING ORDER")
    print("=" * 80)

    service.place_order(order)

    print("Order Saved\n")

    print("=" * 80)
    print("ALL ORDERS")
    print("=" * 80)

    orders = service.get_orders("C0001")

    for order in orders:

        print(order)

    print()

    print("=" * 80)
    print("WEEKLY ORDERS")
    print("=" * 80)

    for order in service.weekly_orders("C0001"):

        print(order)

    print()

    print("=" * 80)
    print("MONTHLY ORDERS")
    print("=" * 80)

    for order in service.monthly_orders("C0001"):

        print(order)

    print()

    print("=" * 80)
    print("YEARLY ORDERS")
    print("=" * 80)

    for order in service.yearly_orders("C0001"):

        print(order)


if __name__ == "__main__":
    main()