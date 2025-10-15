import re
from nltk.tree import Tree
answer = open(r"result.pid","w",encoding="utf-8")

f = open(r"result.txt","r",encoding="utf-8").read().split('\n')

for i in range(len(f)):

    f[i] = f[i].replace('\n','')
    f[i] = re.sub(r"\s+",' ',f[i])
    f[i] = re.sub(r"\) \)",'))',f[i])
    f[i] = re.sub(r"\) \)",'))',f[i])
    f[i] = re.sub(r" \)", ")",f[i])
    f[i] = f[i].split()
    for s in range(len(f[i])-1):
        if '(' in f[i][s] and ')' not in f[i][s+1] and '(' not in f[i][s+1]:
            lst = []
            for index in range(s+1, len(f[i])-1):
                if '(' in f[i][index]:
                    break
                else:
                    lst.append(f[i][index])
            if len(lst) == 1:
                f[i][s+1] = f[i][s+1] + ')'
            else:
                for j in range(len(lst)):
                    f[i][s+1+j] = f[i][s] + ' '+ f[i][s+1+j] + ')'
        elif ')' in f[i][s] and '(' not in f[i][s+1] and ')' not in f[i][s+1]:
            lst = []
            for index in range(s+1, len(f[i])-1):
                if ')' in f[i][index] or '(' in f[i][index]:
                    break
                else:
                    lst.append(f[i][index])
            for j in range(len(lst)):
                f[i][s+1+j] = '( ' + f[i][s+1+j] + ')'
    f[i] = ' '.join(f[i])
    f[i] = re.sub(r"\) \)",'))',f[i])

    lst = f[i].split()
    left_num, right_num = 0, 0
    for j in range(len(lst)-1):
        left_num += lst[j].count('(')
        right_num += lst[j].count(')')
        if left_num <= right_num and j < len(lst) - 2 and lst[j + 1][0] == '(':
            delete_num = right_num - left_num + 1
            lst[j] = lst[j][:-delete_num]
            right_num -= delete_num
    f[i] = ' '.join(lst)





    if f[i].count('(') > f[i].count(')'):
        f[i] += ')' * (f[i].count('(')-f[i].count(')'))
    elif f[i].count('(') < f[i].count(')'):
        f[i] = f[i][:-(f[i].count(')')-f[i].count('('))]
    print(f[i])
    # import pdb;pdb.set_trace()
    t = Tree.fromstring(f[i])
    # print(t)
        
    # if f[i].count('(') > f[i].count(')'):
    #     f[i] += ')' * (f[i].count('(')-f[i].count(')'))
    # elif f[i].count('(') < f[i].count(')'):
    #     f[i] = f[i][:-(f[i].count(')')-f[i].count('('))]
    answer.write(f[i]+'\n')
