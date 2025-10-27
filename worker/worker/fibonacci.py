import asyncio


async def fibonacci_backoff(task, max_attempts):
    a, b = 1, 1
    i = 0

    while i < max_attempts:
        try:
            result = await task()
        except Exception as e:
            print(f"Task failed: {e}")
        else:
            print("Task finished successfully!")
            return result

        print(f"Retrying in {a}s...")
        await asyncio.sleep(a)
        a, b = b, a + b
        i += 1

    print("Max attempts reached, giving up.")
    return None
