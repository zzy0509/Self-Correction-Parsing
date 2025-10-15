
import json
import difflib
import nltk
import openai
import os
import sys
import json
import re
import supar
import nltk
# from nltk.tree import Tree
from supar.utils.metric import SpanMetric
from supar.utils.logging import get_logger
from supar.utils.tokenizer import Tokenizer
from supar.utils.transform import Sentence, Transform
from supar.models.const.crf.transform import Tree

openai.api_key = ""
openai.api_base= ""


def extract_rule(tree):
    rule = ''
    rule += tree.label()
    rule += '->'
    for i in range(len(tree)):
        rule += tree[i].label()
        rule += ' '

    return rule
    

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


def compare_lists(list1, list2):
    # 创建一个SequenceMatcher对象
    matcher = difflib.SequenceMatcher(None, list1, list2)

    # 用于存储差异的列表
    differences = []


    # 对比两个列表，并添加差异到differences列表中
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'delete':
            # differences.append(f"在位置{i1}中删除: {list1[i1:i2]}")
            if i2 - i1 == 1:
                if list1[i1:i2][0] in [',', ':', '``', "''", '.']:
                    continue
                differences.append(["delete", f"({i1}, {i2})", f"Do not additionally add any words to the sentence, such as '{list1[i1:i2][0]}'."])
            else:
                differences.append(["delete", f"({i1}, {i2})", f"Do not additionally add any words to the sentence, such as '{' '.join(list1[i1:i2])}'."])
            # differences.append(["delete", f"({i1}, {i2})", f"Do not make any alterations, especially adding a words, such as '{list1[i1:i2][0]}'."])
        elif tag == 'insert':
            # differences.append(f"在位置{j1}中插入: {list2[j1:j2]}")
            # if list2[j1:j2][0] in [',', ':', '``', "''", '.']:
            #     continue
            if j2 - j1 == 1:
                if list2[j1:j2][0] in [',', ':', '``', "''", '.']:
                    continue
                differences.append(["insert", f"({j1}, {j2})", f"Do not omit '{list2[j1:j2][0]}', as it is considered a single word and should have its own label."])
            else:
                differences.append(["insert", f"({j1}, {j2})", f"Do not omit '{' '.join(list2[j1:j2])}'."])
        elif tag == 'replace':
            if len(list2[j1:j2]) == 1 and ''.join(list1[i1:i2]) == list2[j1:j2][0]:
                differences.append(["replace", f"({i1}, {i2})", f"'{list2[j1:j2][0]}' is considered as one word and should not be separated."])
            elif len(list1[i1:i2]) == 1 and ''.join(list2[j1:j2]) == list1[i1:i2][0]:
                word_num = len(list2[j1:j2])
                words = ' and '.join(list2[j1:j2])
                differences.append(["replace", f"({i1}, {i2})",f"{words} are considered as {word_num} separate words and should be separated with each having its own label."])
            else:
                differences.append(["replace", f"({j1}, {j2})",f"Do not make any changes to the sentence, especially the part '{' '.join(list2[j1:j2])}'."])
                
        elif tag == 'equal':
            pass  # 如果相同则不记录
        else:
            # 如果有拆分或合并的词，可能需要更复杂的逻辑来处理
            pass

    return differences



def word_unmatch(pred_leaves, gold_leaves):
    hint = "Hint: Do not make any changes to any of the words, especially the word "
    differences = []
        # estimate weather word unmatch
    for i in range(len(gold_leaves)):
        if gold_leaves[i] != pred_leaves[i]:
            # differences.append((sentence[i], i))
            differences.append('\'' + gold_leaves[i] + '\'')

    return hint + ', '.join(differences)

def find_sublist(sub, full_list):
    sub_len = len(sub)
    for i in range(len(full_list) - sub_len + 1):
        if full_list[i:i+sub_len] == sub:
            return i
    return -1  # 如果没有找到子列表，则返回-1


prompt = open(r"prompt.txt","r",encoding="utf-8").read()
base = open(r"result.pid","r",encoding="utf-8").read().split('\n')
answer = open(r"result.txt","w",encoding="utf-8")
test = open(r"test.txt","r",encoding="utf-8").read().split('\n')





length_hint = "Hint: Every word that is separated by a space should be considered an independent word and have its own parsing label. "

delete_label = ['TOP', '-NONE-', ',', ':', '``', "''", '.']

count1, count2 = 0, 0
for i in range(len(base)):
    # print( )
    # print(i)
    pred_tree = nltk.Tree.fromstring(base[i])
    gold_tree = nltk.Tree.fromstring(test[i])
    pred_span = Tree.factorize(pred_tree,delete_labels={'TOP', '-NONE-', ',', ':', '``', "''", '.'},equal_labels={'PRT': 'ADVP'})
    gold_span = Tree.factorize(gold_tree,delete_labels={'TOP', '-NONE-', ',', ':', '``', "''", '.'},equal_labels={'PRT': 'ADVP'})
    pred_sentence = pred_tree.leaves()
    # while len(pred_tree) == 1:
    #     pred_tree = pred_tree[0]
    sentence = gold_tree.leaves()
    if (pred_span[-1][:-1] == gold_span[-1][:-1]):
        pred_leaves, gold_leaves = [], []
        for s in pred_tree.subtrees(lambda t: t.height() == 2):
            if s.label() not in delete_label:
                pred_leaves.append(s[0])
        for s in gold_tree.subtrees(lambda t: t.height() == 2):
            if s.label() not in delete_label:
                gold_leaves.append(s[0])
        if pred_leaves == gold_leaves:
            answer.write('TREE'+'\n')
            answer.write(pred_tree.pformat(1e7)+'\n\n')
        else:
            # word unmatch
            print( )
            print('word unmatch')
            Hint= word_unmatch(pred_leaves, gold_leaves)
            print(prompt+' '.join(sentence)+' ('+length_hint+Hint+')'+'\nOutput:')
            answer.write('TREE'+'\n')
            a = replace(prompt+' '.join(sentence)+' ('+length_hint+Hint+')'+'\nOutput:')
            print(a)
            answer.write(a+'\n\n')

    if (pred_span[-1][:-1] != gold_span[-1][:-1]):
        # print(compare_lists(pred_tree.leaves(), sentence))
        count1 += 1
        # print(compare_lists(pred_tree.leaves(), sentence))
        length_unmatch = compare_lists(pred_tree.leaves(), sentence)
        if length_unmatch == []:
            answer.write('TREE'+'\n')
            answer.write(pred_tree.pformat(1e7)+'\n\n')
            continue
        else:
            print( )
            count2 += 1
            lst = []
            for unmatch in length_unmatch:
                tag, word_index, hint = unmatch[0], unmatch[1], unmatch[2]
                lst.append(hint)
            Hint = ' '.join(lst)
            print(prompt+' '.join(sentence)+' ('+length_hint+Hint+')'+'\nOutput:')
            answer.write('TREE'+'\n')
            a = replace(prompt+' '.join(sentence)+' ('+length_hint+Hint+')'+'\nOutput:')
            print(a)
            answer.write(a+'\n\n')



