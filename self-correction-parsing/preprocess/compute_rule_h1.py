from nltk.tree import Tree
import re
import pdb
import json
import random


with open('train.pid', 'r', encoding='utf-8') as fr1:
    trees = [Tree.fromstring(line) for line in fr1]

def extract_rule(tree):
    rule = ''
    rule += tree.label()
    rule += '->'
    for i in range(len(tree)):
        rule += tree[i].label()
        rule += ' '

    return rule


def compute_rule_tree_height_2(trees):

    rule_dict = {}
    dict_count = {}
    for tree in trees:
        sentence = tree.leaves()
        for s in tree.subtrees(lambda t:   t.height() >= 8):
            phrase = s.pformat(1e8)
            rule_lst = []
            rule_string = extract_rule(s)
            dict_count[rule_string] = dict_count.get(rule_string,0) + 1
            if rule_string not in rule_dict.keys():
                rule_dict[rule_string] = [phrase]
            else:
                pre = rule_dict[rule_string]
                if phrase not in pre :
                    new = pre + [phrase]
                    rule_dict[rule_string] = new


    return (rule_dict,dict_count)

ptb_rule = compute_rule_tree_height_2(trees)[0]
print(ptb_rule)


with open("height_1/rule.json","w", encoding='utf-8') as f: ## 设置'utf-8'编码
    f.write(json.dumps(ptb_rule, ensure_ascii=False))