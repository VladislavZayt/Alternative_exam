class CFGrammar:
    def __init__(self, filename=None): 
        self.rules = {}  # Словарь для хранения правил грамматики
        if filename:
            self.load_grammar(filename)  # Загружаем грамматику из файла (формат NON-TERM -> a | b | c | ... )
 
    def load_grammar(self, filename): 
        # Читаем файл и загружаем правила
        with open(filename, 'r', encoding='utf8') as file: 
            for line in file: 
                line = line.strip() 
                if line and not line.startswith('//'): 
                    left, right = line.split(' -> ') 
                    right_parts = [tuple(prod.split()) for prod in right.split(' | ')] 
                    if left not in self.rules: 
                        self.rules[left] = [] 
                    self.rules[left].extend(right_parts) 
 
    def add_rule(self, left, right): 
        # Добавляет правило в грамматику
        if left not in self.rules: 
            self.rules[left] = [] 
        if right not in self.rules[left]: 
            self.rules[left].append(right) 
 
    def get_rules(self, left): 
        # Возвращает правила для указанного левого символа
        return self.rules.get(left, []) 
 
    def print(self): 
        # Выводит правила грамматики в консоль
        for left, right in self.rules.items(): 
            right_side = ' | '.join([' '.join(prod) for prod in right]) 
            print(f"{left} -> {right_side}")

    def is_terminal(self, symbol):
        # Является ли символ терминалом
        return symbol not in self.rules
    
    def to_cnf(self):
        # Преобразует грамматику в нормальную форму Хомского (CNF)
        cnf = CFGrammar() 
        
        # Шаг 1: Добавляем новый стартовый символ, если исходный встречается в правых частях
        start_symbol = next(iter(self.rules)) if self.rules else None
        if start_symbol:
            appears_on_right = False
            for left, rights in self.rules.items():
                for right in rights:
                    if start_symbol in right:
                        appears_on_right = True
                        break
                if appears_on_right:
                    break
            
            if appears_on_right:
                new_start = f"{start_symbol}'"
                cnf.add_rule(new_start, (start_symbol,))
                start_symbol = new_start
        
        # Шаг 2: Удаляем правила с более чем 2 нетерминалами в правой части и обрабатываем терминалы
        terminal_rules = {}  # Словарь для хранения замен терминалов на фиктивные нетерминалы
        next_var_index = 0  # Индекс для фиктивных терминало
        
        for left, rights in self.rules.items():
            for right in rights:
                if not right:
                    continue  # Пропускаем пустые правила (скорее всего, таких не будет)
                
                new_right = [] 
                for symbol in right:
                    if self.is_terminal(symbol) and len(right) > 1:
                        if symbol not in terminal_rules:
                            new_var = f"T_{next_var_index}"
                            next_var_index += 1
                            terminal_rules[symbol] = new_var
                            cnf.add_rule(new_var, (symbol,))
                        new_right.append(terminal_rules[symbol])
                    else:
                        new_right.append(symbol)
                
                if len(new_right) > 2:
                    current_left = left
                    while len(new_right) > 2:
                        new_var = f"X_{next_var_index}"
                        next_var_index += 1
                        cnf.add_rule(current_left, (new_right[0], new_var))
                        current_left = new_var
                        new_right = new_right[1:]
                    cnf.add_rule(current_left, tuple(new_right))
                else:
                    cnf.add_rule(left, tuple(new_right))
        
        # Шаг 3: Удаление unit_productions (единичных правил A -> B, где B - нетерминал)
        unit_productions = []
        for left, rights in cnf.rules.items():
            for right in rights:
                if len(right) == 1 and not self.is_terminal(right[0]):
                    unit_productions.append((left, right[0]))
        
        while unit_productions:
            left, right_nt = unit_productions.pop(0)
            for right in cnf.get_rules(right_nt):
                if len(right) == 1 and not self.is_terminal(right[0]):
                    unit_productions.append((left, right[0]))
                else:
                    cnf.add_rule(left, right)
            
            if (right_nt,) in cnf.rules.get(left, []):
                cnf.rules[left].remove((right_nt,))
        
        cnf.rules = {k: v for k, v in cnf.rules.items() if v}  # Удаляем пустые правила
        
        return cnf

    def save_grammar(self, filename):
        # Сохраняет грамматику в файл
        with open(filename, 'w', encoding='utf8') as file:
            for left, rights in self.rules.items():
                right_side = ' | '.join([' '.join(prod) for prod in rights])
                file.write(f"{left} -> {right_side}\n")