from agents.supervisor.service import SupervisorService


def main():

    service = SupervisorService()

    result = service.execute(

        customer_id="C0001",

        query="Recommend high protein dairy products and tell me how much protein I consumed this month.",

    )

    print(result)


if __name__ == "__main__":

    main()