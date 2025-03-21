from nltk.data import load
import nltk
nltk.download('file:grammar.cfg')
cfg = load('file:grammar.cfg')
print(cfg)