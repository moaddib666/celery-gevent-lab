from tasks import long_task, simple_task


def main_1():
    num_tasks = 1_000  # Dispatch 10 tasks
    for _ in range(num_tasks):
        result = long_task.apply_async()
        print(f"Dispatched Task ID: {result.id}")


def main_2():
    for i in range(10):
        result = simple_task.delay(i)
        print(f"Dispatched Task {result.id}")


if __name__ == "__main__":
    main_2()
