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

def get_daughter(tree):

    daughter = []
    for i in range(len(tree)):
        daughter.append(' '.join(tree[i].leaves()))
    
    return daughter

def get_label(tree):

    label = [tree.label()]
    for i in range(len(tree)):
        label.append(tree[i].label())
    
    return label



with open(r"rule.json","r", encoding='utf-8') as f_rule:
    rule_dict = json.load(f_rule)

predict = open(r"result.pid","r",encoding="utf-8").read().split('\n')
gold = open(r"test.pid","r",encoding="utf-8").read().split('\n')


count = 0
correct = 0
wrong = 0
known = 0
correct_yield = 0
wrong_yield = 0
label_error, flatness_error, deepness_error, span_error = 0, 0, 0, 0
for i in range(len(predict)):
    # print( )
    # print(i)
    pred_tree = nltk.Tree.fromstring(predict[i])
    gold_tree = nltk.Tree.fromstring(gold[i])[0]
    for s in pred_tree.subtrees(lambda t:  t.height() >= 3):
        phrase = ' '.join(s.leaves())
        pred_daughter = get_daughter(s)
        pred_label = get_label(s)
        flag = False
        for g in gold_tree.subtrees():
            if ' '.join(g.leaves()) == phrase and flag == False:
                flag = True
                if g.height() > 2:
                    gold_daughter = get_daughter(g)
                    gold_label = get_label(g)
                else:
                    # print(s.pformat(1e6),pred_label,g.pformat(1e6))
                    gold_daughter = g.leaves()
                    gold_label = g.label()
                if gold_daughter == pred_daughter and gold_label != pred_label:
                    label_error += 1
                elif len(pred_daughter) < len(gold_daughter):
                    deepness_error += 1
                else:
                    flatness_error += 1

        if flag == False:
            span_error += 1

wrong_num = label_error + flatness_error + deepness_error + span_error
print(wrong_num)
