import cfg, cky_parser

def main():
    grammar = cfg.CFGrammar('rus_parse//cfgrammar.txt').to_cnf()
    parser = cky_parser.CKYParser(grammar)

    while True:
        sentence = input("Введите предложение для разбора: ").lower().split(' ')
        can_parse, parse_table, backpointers = parser.parse(sentence)

        if can_parse:
            print("Предложение может быть разобрано.")
            # Восстанавливаем и выводим дерево разбора
            parse_tree = parser.extract_parse_tree(sentence, parse_table, backpointers)
            parser.print_parse_tree(parse_tree)
        else:
            print("Предложение не может быть разобрано.")
            print("\nУзнанные составляющие: ")
            n = len(sentence)
            for i in range(n):
                for j in range(i+1, n+1):
                    if parse_table[i][j]:
                        constituent = " ".join(sentence[i:j])
                        labels = ", ".join(sorted(parse_table[i][j]))
                        print(f"'{constituent}'")

if __name__ == "__main__":
    main()