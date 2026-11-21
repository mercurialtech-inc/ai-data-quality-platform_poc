def retry(max_attempts):

    def decorator(func):

        def wrapper():
            for attempt in range(max_attempts):
                try:
                    return func()
                except ConnectionError:
                    if attempt == max_attempts - 1:
                        raise
                    print("Retrying...")

        return wrapper

    return decorator