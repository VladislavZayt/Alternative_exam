
class CKYParser:
    def __init__(self, grammar):
        # grammar  - Грамматика в нормальной форме Хомского (CNF)
        self.grammar = grammar
    
    def parse(self, sentence):
        """
        Реализует алгоритм CKY для синтаксического анализа предложения.
        sentence -  Список токенов (слов) предложения
        """
        if not all(len(right) <= 2 for rights in self.grammar.rules.values() for right in rights):
            raise ValueError("Грамматика должна быть в форме Хомского для CKY-разбора")
        
        n = len(sentence)
        table = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        back = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        # Заполняем диагональ (слова)
        for i in range(n):
            word = sentence[i]
            for left, rights in self.grammar.rules.items():
                for right in rights:
                    if len(right) == 1 and right[0] == word:
                        table[i][i+1].add(left)
        
        # Заполняем оставшуюся таблицу
        for length in range(2, n + 1):  # Длина отрезка
            for i in range(n - length + 1):  # Начало отрезка
                j = i + length  # Конец отрезка
                
                for k in range(i + 1, j):  # Возможные разбиения
                    for left, rights in self.grammar.rules.items():
                        for right in rights:
                            if len(right) == 2: 
                                B, C = right
                                if B in table[i][k] and C in table[k][j]:
                                    table[i][j].add(left)
                                    if left not in back[i][j]:
                                        back[i][j][left] = []
                                    back[i][j][left].append((B, C, k))
        
        start_symbol = next(iter(self.grammar.rules)) if self.grammar.rules else None
        can_parse = start_symbol in table[0][n]
        
        return can_parse, table, back
    
    def extract_parse_tree(self, sentence, parse_table, backpointers):
        """
        Восстанавливает дерево разбора из CKY-таблицы.
        sentence: Входное предложение (список токенов)
        parse_table: Заполненная CKY-таблица
        backpointers: Указатели для восстановления дерева
        :return: Вложенный кортеж, представляющий дерево разбора, или None
        """
        n = len(sentence)
        start_symbol = next(iter(self.grammar.rules)) if self.grammar.rules else None
        
        if not start_symbol or start_symbol not in parse_table[0][n]:
            return None
        
        def build_tree(symbol, i, j):
            if j - i == 1:
                return (symbol, sentence[i])
            
            if symbol not in backpointers[i][j]:
                return None
            
            B, C, k = backpointers[i][j][symbol][0]
            left_tree = build_tree(B, i, k)
            right_tree = build_tree(C, k, j)
            
            return (symbol, left_tree, right_tree)
        
        return build_tree(start_symbol, 0, n)
    
    def print_parse_tree(self, tree, indent=0):
        """
        Выводит в консоль дерево разбора.
        tree: Вложенный кортеж, представляющий дерево разбора
        indent: уровень отступа для отображения вложенности
        """
        if tree is None:
            print(" " * indent + "None")
            return
        
        if isinstance(tree, tuple):
            if len(tree) == 2 and isinstance(tree[1], str):
                print(" " * indent + f"{tree[0]} -> {tree[1]}")
            else:
                print(" " * indent + f"{tree[0]}")
                for subtree in tree[1:]:
                    self.print_parse_tree(subtree, indent + 2)
        else:
            print(" " * indent + str(tree))