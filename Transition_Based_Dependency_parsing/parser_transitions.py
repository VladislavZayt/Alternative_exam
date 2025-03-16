class PartialParse(object): # реализация парсера на основе переходов
    def __init__(self, sentence):
        self.sentence = sentence
        self.stack = ["ROOT"]
        self.buffer = [i for i in sentence]
        self.dependencies = []


    def parse_step(self, transition): # шаг алгоритма 
        if transition == "S": #Shift
            try:
                self.stack.append(self.buffer.pop(0))
            except:
                print("Невозможно перенести слово из буфера в стек!")
        elif transition == "LA": #Left Arc
            try:
                self.dependencies.append((self.stack[-1], self.stack.pop(-2)))
            except:
                print("Невозможно установить левую зависимость!")
        elif transition == "RA": #Right Arc
            try:
                self.dependencies.append((self.stack[-2], self.stack.pop(-1)))
            except Exception as e:
                print("Stack size: ", len(self.stack))
                print("Невозможно установить правую зависимость!", e)
        else:
            pass

    def parse(self, transitions): # парсинг
        for transition in transitions:
            self.parse_step(transition)
        return self.dependencies

def minibatch_parse(sentences, model, batch_size): # анализ предложений
    dependencies = []
    partial_parses = list(map(lambda x: PartialParse(x), sentences)) # список объектов типа PartialParse 
    unfinished_parses = partial_parses[:] # копия partial_parses
    while unfinished_parses:
        transitions = model.predict(unfinished_parses[:batch_size])
        for parse, transition in zip(unfinished_parses[:batch_size], transitions):
            parse.parse_step(transition)
            if len(parse.stack) == 1 and len(parse.buffer) == 0:
                unfinished_parses = [x for x in unfinished_parses if x!= parse]
    dependencies = [i.dependencies for i in partial_parses]

    return dependencies