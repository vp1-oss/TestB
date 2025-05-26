def fibonacci_recursive(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

# Generate the first 100 Fibonacci numbers using recursion
fibonacci_numbers = [fibonacci_recursive(i) for i in range(100)]

# Write to file
with open("fibonacci_recursive_output.txt", "w") as f:
    f.write("Fibonacci numbers (Recursive):\n")
    f.write(", ".join(map(str, fibonacci_numbers)))

print("Recursive Fibonacci numbers written to 'fibonacci_recursive_output.txt'.")
