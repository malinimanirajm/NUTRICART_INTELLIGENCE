"""
test_nutrition.py
"""

from agents.nutrition.service import NutritionService


def print_report(report):

    print("=" * 80)
    print(f"{report.period.upper()} NUTRITION SUMMARY")
    print("=" * 80)

    print(f"Orders      : {report.total_orders}")
    print(f"Protein     : {report.summary.protein:.2f} g")
    print(f"Calories    : {report.summary.calories:.2f} kcal")
    print(f"Sugar       : {report.summary.sugar:.2f} g")
    print(f"Fat         : {report.summary.fat:.2f} g")
    print(f"Fiber       : {report.summary.fiber:.2f} g")
    print(f"Sodium      : {report.summary.sodium:.2f} mg")
    print(f"Potassium   : {report.summary.potassium:.2f} mg")

    print()


def main():

    customer_id = "C00101"

    service = NutritionService()

    print_report(
        service.daily_summary(customer_id)
    )

    print_report(
        service.weekly_summary(customer_id)
    )

    print_report(
        service.monthly_summary(customer_id)
    )

    print_report(
        service.yearly_summary(customer_id)
    )


if __name__ == "__main__":
    main()