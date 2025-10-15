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


with open("rule.json","r", encoding='utf-8') as f_rule:
    rule_dict = json.load(f_rule)


predict = open(r"result.txt","r",encoding="utf-8").read().split('\n')
gold = open(r"/test.pid","r",encoding="utf-8").read().split('\n')
count = 0
correct = 0
wrong = 0
known = 0
correct_yield = 0
wrong_yield = 0
unknown = 0
for i in range(len(predict)):
    pred_tree = nltk.Tree.fromstring(predict[i])
    gold_tree = nltk.Tree.fromstring(gold[i])
    for g in gold_tree.subtrees(lambda t: t.height() > 2):
        phrase = ' '.join(g.leaves())
        gold_daughter = get_daughter(g)
        gold_label = get_label(g)
        if compute_rule(g) not in rule_dict:
            unknown += 1
            for s in pred_tree.subtrees(lambda t: t.height() > 2):
                if ' '.join(s.leaves()) == phrase:
                    pred_daughter = get_daughter(s)
                    pred_label = get_label(s) 
                    if  len(pred_daughter) == len(gold_daughter) and gold_label == pred_label: 
                        correct += 1               
print(unknown)
print(correct)
print(correct/unknown)