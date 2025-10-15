import json
import difflib
import nltk
import openai
import re
import random
import time
from copy import deepcopy

openai.api_key = ""
openai.api_base=""


with open("rule.json","r", encoding='utf-8') as f_rule:
    rule_dict = json.load(f_rule)

with open("height_1/rule.json","r", encoding='utf-8') as f_rule_height_1:
    rule_dict_height_1 = json.load(f_rule_height_1)


with open("height_2/rule.json","r", encoding='utf-8') as f_rule_height_2_v1:
    rule_dict_height_2 = json.load(f_rule_height_2_v1)


with open("rule_count.json","r", encoding='utf-8') as f_rule_count:
    rule_count = json.load(f_rule_count)



def extract_rule(tree):
    rule = ''
    rule += tree.label()
    rule += '->'
    for i in range(len(tree)):
        rule += tree[i].label()
        rule += ' '

    return rule

def extract_height_h1(tree):
    
    for i in range(len(tree)):
        if tree[i].height() == 2:
            tree[i] = nltk.Tree.fromstring('('+tree[i].label()+' word'+')')
        else:
            tree[i] = nltk.Tree.fromstring('('+tree[i].label()+' phrase'+')')

    return tree 

def compute_rule_height_2(tree):

    rule_lst = []
    Height = tree.height()
    for subtree in tree.subtrees(lambda t : t.height() >= Height - 1):
        rule_lst.append(extract_rule(subtree))
    rule_string = ', '.join(rule_lst)

    return rule_string 


def compute_rule(tree):

    rule_lst = []
    for subtree in tree.subtrees(lambda t : t.height() > 2):
        rule_lst.append(extract_rule(subtree))
    rule_string = ', '.join(rule_lst)

    return rule_string


def replace(prompt):
    while True:
        try:
            message = [{'role':'user','content':prompt}]
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages = message,
                max_tokens=2000,
                temperature=0,
                stop=None)
            generated_text = response.choices[0].message.content
            break
        except:
            pass

    return generated_text

    
def simple_rule(tree):


    if tree.height() <= 2:
        label_lst = []
        for s in tree.subtrees(lambda t: t.height() >= 2):
            label_lst.append(s.label())
        return label_lst
    else:
        label_lst = []
        for i in range(len(tree)):
            if tree[i].height() == 2 and tree[i][0] == 'word':
                label_lst.append('POS:'+tree[i].label())
            elif tree[i].height() == 2 and tree[i][0] == 'phrase':
                label_lst.append(tree[i].label())
            else:
                label_lst += simple_rule(tree[i])
        # print(label_lst)
        return label_lst

def extract_height_h2(tree,index):
    

    for i in range(len(tree)):
        if tree[i].height() == 2:
            tree[i] = nltk.Tree.fromstring('('+tree[i].label()+' word'+')')
        else:
            if i == index:
                for j in range(len(tree[i])):
                    if tree[i][j].height() == 2:
                        tree[i][j] = nltk.Tree.fromstring('('+tree[i][j].label()+' word'+')')
                    else:
                        tree[i][j] = nltk.Tree.fromstring('('+tree[i][j].label()+' phrase'+')')
            else:
                tree[i] = nltk.Tree.fromstring('('+tree[i].label()+' phrase'+')')

    
    return tree  

def height_h2(tree,index_lst):

    tree_lst = []

    for i in index_lst:
        if tree[i].height() > 2:
            new_tree = deepcopy(tree)
            tree_lst.append(extract_height_h2(new_tree,i))

    return tree_lst

def get_daughter_label(tree):

    label_lst = []
    for subtree in tree:
        label_lst.append(subtree.label())

    return label_lst
    

def check_rule_v1(new_t, new_s):


    s_label = []
    for subtree in new_s.subtrees(lambda tree: tree.height() >= 2 and tree[0] != 'word'):
        s_label.append(subtree.label())

    if new_s.label() != new_t.label():
        return False
    t_label = []
    for subtree in new_t.subtrees(lambda tree: tree.height() >= 2 and tree[0] != 'word'):
        t_label.append(subtree.label())

    label_dif = 0
    for i in range(min(len(s_label), len(t_label))):
        if t_label[i] not in s_label:
            label_dif += 1
            
    if label_dif > 1:
        return False

    simple_s = simple_rule(new_s)
    simple_t = simple_rule(new_t)
    dif = 0
    # if len(simple_t) < len(simple_s):
    #     return False
    for i in range(min(len(simple_s),len(simple_t))):
        if simple_s[i] != simple_t[i]:
            if 'POS' not in simple_s[i] :
                return False
            else:
                dif += 1
    if dif > 1:
        return False
    if lcs(simple_s,simple_t) == 1:
        return False
    return lcs(simple_s,simple_t)


def lcs(s, t):
    len1 = len(s)
    len2 = len(t)
    # 初始化一个二维数组，行数为t的大小，列数为s的大小
    res = [[0 for i in range(len1 + 1)] for j in range(len2 + 1)]
    for i in range(1, len2 + 1):
        for j in range(1, len1 + 1):
            if t[i - 1] == s[j - 1]:
                res[i][j] = 1 + res[i - 1][j - 1]
            else:
                res[i][j] = max(res[i - 1][j], res[i][j - 1])
    return res[-1][-1]


def LCS(seq1, seq2):
    # 初始化表格
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 填充表格
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 追踪最长公共子序列及其下标
    lcs = []
    indexes1 = []
    indexes2 = []
    i, j = m, n

    while i > 0 and j > 0:
        if seq1[i - 1] == seq2[j - 1]:
            lcs.append(seq1[i - 1])
            indexes1.append(i - 1)
            indexes2.append(j - 1)
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    # 由于我们是从后向前追踪的，最终结果需要反转
    lcs = lcs[::-1]
    indexes1 = indexes1[::-1]
    indexes2 = indexes2[::-1]

    return lcs, indexes1, indexes2



def select_example(rule, s):
    same_word = 0
    example = rule_dict_height_2[rule][0]
    phrase = s.leaves()
    for i in rule_dict_height_2[rule]:
        
        t = nltk.Tree.fromstring(i)
        if lcs(phrase, t.leaves()) > same_word:
            example = i


    return example


def delete_example(select_rule):
    rule_lst = select_rule[0][0]
    new_lst = select_rule[0]
    for i in select_rule:
        rule = i[0]
        t = rule_dict[rule][0]
        if compute_rule(t[0]) not in rule_lst:
            new_lst.append(i)
            rule_lst.append(rule)
    return(new_lst)


def find_flatness_error_rules(s, t, mode):

    if mode == 'h1':


        index_lst = [i for i in range(len(t))]

        new_s = deepcopy(s)
        new_s = extract_height_h1(new_s)
        t_lst = height_h2(t, index_lst)
    # else:

    for j in range(len(t_lst)):
        if check_rule_v1(t_lst[j], new_s) != False:
            t_lst[j] = (t_lst[j], check_rule_v1(t_lst[j], new_s))
        else:
            t_lst[j] = (t_lst[j], 0)
    t_lst = sorted(t_lst, key=lambda x:x[1],reverse=True)

    if len(t_lst) > 0:
        return t_lst[0][1]

    else:
        return 0
    

    
def find_hierarchy_error_rules(s, t , mode):

    if mode == 'h1':

        index_lst = [i for i in range(len(s))]
        new_t = deepcopy(t)
        new_t = extract_height_h1(new_t)
        s_lst = height_h2(s, index_lst)

    for j in range(len(s_lst)):
        if check_rule_v1(new_t,s_lst[j]) != False:
            s_lst[j] = (s_lst[j], check_rule_v1(new_t,s_lst[j]))
        else:
            s_lst[j] = (s_lst[j], 0)
    s_lst = sorted(s_lst, key=lambda x:x[1],reverse=True)

    if len(s_lst) > 0:
        return s_lst[0][1]
    else:
        return 0
    

def find_label_error_rules(s, t, mode):

    if mode == 'h1':

        new_s, new_t = deepcopy(s), deepcopy(t)
        new_s, new_t = extract_height_h1(new_s), extract_height_h1(new_t)

    if check_rule_v1(new_t, new_s) != False:
        return check_rule_v1(new_t, new_s)
    else:
        return 0






def find_rules_h1(s):

    flatness_rule, hierarchy_rule, label_rule = [], [], []
    temp, candidate_rule = [], []
    for rule in rule_dict_height_2:
        if len(rule_dict_height_2[rule]) <= 5:
            continue
        t = nltk.Tree.fromstring(rule_dict_height_2[rule][0])
        if t.label() == s.label():
            # print(s)
            if len(s) > len(t):
                error_lcs = find_flatness_error_rules(s, t, mode='h1')
                if error_lcs > 2:
                    flatness_rule.append((rule, error_lcs ,len(rule_dict_height_2[rule])))
            elif len(s) < len(t):
                error_lcs = find_hierarchy_error_rules(s, t, mode='h1')
                if error_lcs  > 2:
                    hierarchy_rule.append((rule, error_lcs,len(rule_dict_height_2[rule]) ))
            else:
                error_lcs = find_label_error_rules(s, t, mode='h1')
                if error_lcs  > 2:
                    label_rule.append((rule, error_lcs,len(rule_dict_height_2[rule])))

    flatness_rule = sorted(flatness_rule, key=lambda x : (x[1],x[2]), reverse=True )[:10]
    hierarchy_rule = sorted(hierarchy_rule, key=lambda x : (x[1],x[2]), reverse=True )[:10]
    label_rule = sorted(label_rule, key=lambda x : (x[1],x[2]), reverse=True )[:10]    
    temp = flatness_rule + hierarchy_rule + label_rule    
    temp = sorted(temp, key=lambda x : (x[1],x[2]), reverse=True ) 
    for can in temp:
        if can not in candidate_rule:
            candidate_rule.append(can)

    return candidate_rule[:5]  



prompt = open(r"prompt.txt","r",encoding="utf-8").read()
base = open(r"height_10.txt","r",encoding="utf-8").read().split('\n')
answer = open(r"height_9.txt","w",encoding="utf-8")
test_answer = open(r"all.pid","r",encoding="utf-8").read().split('\n')


Hint = " (Hint: Are there any phrases with similar structures in the example? If there are, please follow the example; if not, please answer according to the grammatical structure. Every word that is separated by a space should be considered an independent word and have its own parsing label.)"




H = 9
T = 0
count = 0
for i in range(len(base)):
    pred_tree = nltk.Tree.fromstring(base[i])
    pred_sentence = pred_tree.leaves()
    gold_tree = nltk.Tree.fromstring(test_answer[i])[0]
    sentence = gold_tree.leaves()
    for s in pred_tree.subtrees(lambda t: t.height() == H):
        rule_height_1 = extract_rule(s)
        rule_height_2 = compute_rule_height_2(s)
        phrase = ' '.join(s.leaves())
        if rule_height_1 not in rule_dict_height_1:    
            example_lst = []
            candidate_rule = find_rules_h1(s)

            for can in  candidate_rule:
                rule = can[0]
                example_lst.append((rule,select_example(rule,s)))
            example_lst = example_lst[::-1]
            example = ''
            for e in example_lst:
                t = e[1]
                ph = ' '.join(nltk.Tree.fromstring(t).leaves())
                example += 'phrase: ' + ph + '\n' + 'parse tree: ' + t + '\n' 

            if '(parse tree: ' in a:
                a = a[13:-1]
            a = a.replace('\n','')
            a = re.sub(r"\s+",' ',a)
            a = re.sub(r"\) \)",'))',a)
            a = re.sub(r"\) \)",'))',a)
            print(a)
            if a[0] != '(':
                a = a[a.index('('):]
            if a[-1] != ')':
                a = a[:-a[::-1].index(')')]
            if a.count('(') > a.count(')'):
                a += ')' * (a.count('(')-a.count(')'))
            elif a.count('(') < a.count(')'):
                a = a[:-(a.count(')')-a.count('('))]
            base[i] = base[i].replace(s.pformat(1e7),a)

    answer.write(base[i]+'\n')