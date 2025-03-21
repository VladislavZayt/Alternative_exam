import nltk
from nltk.corpus import treebank
import re

def clean_nonterm(nonterm):
    return re.sub(r'\|<.*?>', '', nonterm)

def cfg_from_treebank():
    nltk.download("treebank")
    grammar = {}
    for tree in treebank.parsed_sents():
        tree.chomsky_normal_form()  
        productions = tree.productions()
        for prod in productions:
            lhs = clean_nonterm(str(prod.lhs()))  
            rhs = tuple(clean_nonterm(str(sym)) for sym in prod.rhs())  

            if lhs not in grammar:
                grammar[lhs] = set()
            grammar[lhs].add(rhs)

    return grammar

def save_grammar(grammar, filename="eng_parse//cf_grammar.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for lhs, rhs_list in grammar.items():
            rhs_str = " | ".join([" ".join(rhs) for rhs in rhs_list])
            f.write(f"{lhs} -> {rhs_str}\n")