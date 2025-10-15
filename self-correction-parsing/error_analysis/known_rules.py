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


with open("rule.json","r", encoding='utf-8') as f_rule:
    rule_dict = json.load(f_rule)



predict = open(r"berkeley_test.pid","r",encoding="utf-8").read().split('\n')
gold = open(r"test.pid","r",encoding="utf-8").read().split('\n')


count = 0
correct = 0
wrong = 0
known = 0
correct_yield = 0
wrong_yield = 0
for i in range(len(predict)):
    # print( )
    # print(i)
    pred_tree = nltk.Tree.fromstring(predict[i])
    gold_tree = nltk.Tree.fromstring(gold[i])
    pred_phrase = []
    gold_phrase = []
    pred_subtree = []
    gold_subtree = []
    for s in pred_tree.subtrees(lambda t: t.height() > 2):
        count += 1
        if compute_rule(s) in rule_dict:
            known += 1
            if s.pformat(1e6) in gold[i]:
                correct += 1
            else:
                wrong += 1
                flag = False
                for g in gold_tree.subtrees():
                    if ' '.join(g.leaves()) == ' '.join(s.leaves()):
                        flag = True
                if flag:
                    correct_yield += 1
                else:
                    wrong_yield += 1

print(count)
print(known)
print(correct,correct/known)
print(wrong,wrong/known)
print(correct_yield/wrong,wrong_yield/wrong)