from datetime import datetime
import os
import math
import time
import argparse

from torch import nn, optim
import torch
from tqdm import tqdm


import matplotlib.pyplot as plt
import networkx as nx

from parser_model import ParserModel
from utils.parser_utils import minibatches, load_and_preprocess_data, AverageMeter, load_empty_model

parser = argparse.ArgumentParser(description='Train neural dependency parser in pytorch')
parser.add_argument('-d', '--debug', action='store_true', help='whether to enter debug mode')
args = parser.parse_args()

def train(parser, train_data, dev_data, output_path, batch_size=1024, n_epochs=10, lr=0.0005):
    best_dev_UAS = 0
    optimizer = optim.Adam(parser.model.parameters(), lr = lr)
    loss_func = nn.CrossEntropyLoss(reduction = 'mean')

    for epoch in range(n_epochs):
        print("Epoch {:} out of {:}".format(epoch + 1, n_epochs))
        dev_UAS = train_for_epoch(parser, train_data, dev_data, optimizer, loss_func, batch_size)
        if dev_UAS > best_dev_UAS:
            best_dev_UAS = dev_UAS
            print("New best dev UAS! Saving model.")
            torch.save(parser.model.state_dict(), output_path)
        print("")

def train_for_epoch(parser, train_data, dev_data, optimizer, loss_func, batch_size):
    parser.model.train()
    n_minibatches = math.ceil(len(train_data) / batch_size)
    loss_meter = AverageMeter()
    with tqdm(total=(n_minibatches)) as prog:
        for i, (train_x, train_y) in enumerate(minibatches(train_data, batch_size)):
            optimizer.zero_grad()   # remove any baggage in the optimizer
            loss = 0. # store loss for this batch here
            train_x = torch.from_numpy(train_x).long()
            train_y = torch.from_numpy(train_y.nonzero()[1]).long()
            output = parser.model(train_x)
            loss = loss_func(output, train_y)
            loss.backward()
            optimizer.step()

            prog.update(1)
            loss_meter.update(loss.item())

    print ("Average Train Loss: {}".format(loss_meter.avg))
    print("Evaluating on dev set",)
    parser.model.eval()
    dev_UAS, _ = parser.parse(dev_data)
    print("- dev UAS: {:.2f}".format(dev_UAS * 100.0))
    return dev_UAS

def complete_training():
    debug = args.debug

    assert (torch.__version__.split(".") >= ["1", "0", "0"]), "Please install torch version >= 1.0.0"

    parser, embeddings, train_data, dev_data, test_data= load_and_preprocess_data(debug)
    start = time.time()
    model = ParserModel(embeddings) 

    parser.model = model
    output_dir = "results/{:%Y%m%d_%H%M%S}/".format(datetime.now())
    output_path = output_dir + "model.weights"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    train(parser, train_data, dev_data, output_path, batch_size=1024, n_epochs=10, lr=0.0005)


def draw_dependency_tree(dependencies):
    G = nx.DiGraph()
    for head, dependent in dependencies:
        G.add_edge(head, dependent)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, arrows=True, node_size=2000, node_color='lightblue', font_size=10, font_color='black')
    plt.title("Dependency Tree")
    plt.show()

if __name__ == "__main__":
    parser, embeddings = load_empty_model()
    start = time.time()
    model = ParserModel(embeddings)
    
    relative_path = os.path.join("results", "20250317_214836", "model.weights")
    model.load_state_dict(torch.load(relative_path, weights_only=True))

    parser.model = model
    while True:
        input_sentence = parser.read_str(str(input()))

        dependencies = parser.predict(input_sentence)

        d = parser.devectorize(input_sentence)
        for depend in sorted(dependencies[0]):
                print(d[depend[0]], d[depend[1]])

        labeled_dependencies = [(d[head], d[dependent]) for head, dependent in dependencies[0]]
        draw_dependency_tree(labeled_dependencies)