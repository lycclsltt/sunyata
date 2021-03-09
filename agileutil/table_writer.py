#coding=utf-8
'''
生成表格

用法：

header = ['name', 'age']
rows = [ ['wangermazi', 25], ['zhangsan', 11], ['lisi', 30] ]
tbWriter = TableWriter(header, rows)
tbWriter.dump()
string = tbWriter.getString()
print(string)

+--------------+-------+
|  name        |  age  |
+--------------+-------+
|  wangermazi  |  25   |
|  zhangsan    |  11   |
|  lisi        |  30   |
+--------------+-------+
'''


class TableWriter:
    def __init__(self, header=[], rows=[], lWidth=2, rWidth=2):
        if type(header) != list or type(rows) != list:
            raise Exception('param headers, rows must be list type')

        self._maxCol = len(header)
        for row in rows:
            if len(row) > self._maxCol:
                self._maxCol = len(row)

        self._header = header
        self._rows = rows
        self._colMaxLengthList = self._getColsMaxLength()
        self._lWidth = lWidth
        self._rWidth = rWidth

    def _getColsMaxLength(self):
        allRows = []
        allRows.append(self._header)
        for row in self._rows:
            allRows.append(row)

        colMaxLengthList = []
        for i in range(self._maxCol):
            colMaxLength = 0

            for row in allRows:
                try:
                    fieldLength = len(str(row[i]))
                except:
                    continue
                if fieldLength > colMaxLength:
                    colMaxLength = fieldLength

            colMaxLengthList.append(colMaxLength)

        return colMaxLengthList

    def _genFieldStr(self, string, maxLength):
        string = str(string)
        restSpaceLength = maxLength - len(string)
        ret = ''.join([' ' for i in range(self._lWidth)])
        ret = ret + string + ''.join(
            [' ' for i in range(restSpaceLength + self._rWidth)])
        return ret

    def getString(self):
        headerFieldList = []
        for i in range(len(self._header)):
            fieldStr = self._genFieldStr(self._header[i],
                                         self._colMaxLengthList[i])
            headerFieldList.append(fieldStr)
        headerStr = '|' + '|'.join(headerFieldList) + '|' + "\n"

        rowListStr = ''
        for row in self._rows:
            rowFieldList = []
            for i in range(len(row)):
                fieldStr = self._genFieldStr(row[i], self._colMaxLengthList[i])
                rowFieldList.append(fieldStr)
            rowStr = '|' + '|'.join(rowFieldList) + '|'
            rowListStr = rowListStr + rowStr + "\n"

        indentList = []
        for maxLength in self._colMaxLengthList:
            fieldStr = ''.join(
                ['-' for i in range(maxLength + self._lWidth + self._rWidth)])
            indentList.append(fieldStr)
        indentStr = '+' + '+'.join(indentList) + '+' + "\n"

        ret = ''
        if len(self._header) > 0:
            ret = ret + indentStr + headerStr + indentStr
        if len(self._rows) > 0:
            ret = ret + rowListStr + indentStr

        return ret

    def dump(self):
        print(self.getString())
