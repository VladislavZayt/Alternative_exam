import cfg, cky_parser
from grammar_from_treebank import cfg_from_treebank, save_grammar

def main():
    # grammar = cfg_from_treebank()
    # save_grammar(grammar)
    # grammar = cfg.CFGrammar('eng_parse//cfgrammar.txt').to_cnf()
    # grammar.save_grammar("eng_parse//cnf_grammar.txt")
    grammar = cfg.CFGrammar("eng_parse//cnf_grammar.txt")
    parser = cky_parser.CKYParser(grammar)
    while True:
        sentence = input("Enter sentence to parse: ").split(' ')
        can_parse, parse_table, backpointers = parser.parse(sentence)
        if can_parse:
            print("Sentence can be parsed.")
            parse_tree = parser.extract_parse_tree(sentence, parse_table, backpointers)
            parser.print_parse_tree(parse_tree)
        else:
            print("Sentence cannot be parsed.")
            n = len(sentence)
            print("\nRecognized constituents:")
            for i in range(n):
                for j in range(i+1, n+1):
                    if parse_table[i][j]:
                        constituent = " ".join(sentence[i:j])
                        labels = ", ".join(sorted(parse_table[i][j]))
                        print(f"'{constituent}'")

if __name__ == "__main__":
    main()