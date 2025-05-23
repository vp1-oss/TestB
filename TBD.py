def binary_search_iterative(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2

        if arr[mid] == target:
            return mid  # Target found at index mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1  # Target not found


# Example usage
arr = [1, 3, 5, 7, 9, 11]
target = 7
print(binary_search_iterative(arr, target))  # Output: 3
