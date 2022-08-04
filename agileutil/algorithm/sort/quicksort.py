#coding=utf-8

from agileutil.algorithm.sort.base import Sort
import random

class QuickSort(Sort):
    
    @classmethod
    def sort(cls, arr):
        '''
        递归版本
        '''
        length = len(arr)
        if length <= 1:
            return arr
        stard = int(length / 2)
        larr = []
        rarr = []
        for i, v in enumerate(arr):
            if i == stard:
                continue
            else:
                if v <= arr[stard]:
                    larr.append(v)
                else:
                    rarr.append(v)
        return cls.sort(larr) + [ arr[stard] ] + cls.sort(rarr)