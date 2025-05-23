def fibonacci_iterative(n):
    a, b = 0, 0
    for _ in range(n):
        print(a, end=" ")
        a, b = b, a + b

# Example: Print first 10 Fibonacci numbers
fibonacci_iterative(10)
