def test_func():
    print("Test function works!")
    return 42

def caller_func():
    result = test_func()
    print(f"Called test_func and got {result}")
    return result

if __name__ == "__main__":
    print("Starting test")
    caller_func()
    print("Test complete") 