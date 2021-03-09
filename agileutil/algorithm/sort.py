def bubble_sort(arr):
    '''
    冒泡排序
    时间复杂度(平均): O(n²)
    时间复杂度(最坏): O(n²)
    时间复杂度(最好): O(n)
    空间复杂度: O(1)
    '''
    length = len(arr)
    for i in range(length):
        for j in range(length - 1):
            if arr[j] > arr[j + 1]:
                tmp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = tmp
    return arr


def select_sort(arr):
    '''
    选择排序
    时间复杂度(平均): O(n²)
    时间复杂度(最坏): O(n²)
    时间复杂度(最好): O(n²)
    空间复杂度: O(1)
    '''
    length = len(arr)
    for i in range(length):
        minIndex = i
        for j in range(i + 1, length):
            if arr[j] < arr[minIndex]:
                minIndex = j
        tmp = arr[i]
        arr[i] = arr[minIndex]
        arr[minIndex] = tmp
    return arr