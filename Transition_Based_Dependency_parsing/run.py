from datetime import datetime
import os
import pickle
import math
import time
import argparse

from torch import nn, optim
import torch
from tqdm import tqdm

from parser_model import ParserModel
from utils.parser_utils import minibatches, load_and_preprocess_data, AverageMeter

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


if __name__ == "__main__":
    debug = args.debug

    assert (torch.__version__.split(".") >= ["1", "0", "0"]), "Please install torch version >= 1.0.0"

    
    
    print(80 * "=")
    print("INITIALIZING")
    print(80 * "=")
    parser, embeddings, train_data, dev_data, test_data = load_and_preprocess_data(debug)
    
    start = time.time()
    model = ParserModel(embeddings)
    parser.model = model
    print("took {:.2f} seconds\n".format(time.time() - start))
    
    test_sent = parser.read_str("The quick brown fox jumps over the lazy dog.")
    test_sent2 = parser.read_str("She sells seashells by the seashore.")
    test_sent3 = parser.read_str("The cat sat on the mat while the dog barked loudly.")

    tests = [test_sent, test_sent2, test_sent3]
    print(80 * "=")
    print("TRAINING")
    print(80 * "=")
    output_dir = "results/{:%Y%m%d_%H%M%S}/".format(datetime.now())
    output_path = output_dir + "model.weights"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    train(parser, train_data, dev_data, output_path, batch_size=1024, n_epochs=1, lr=0.0005)
    
    for i in range(0, len(tests)):
        print(tests[i])
        
        dependencies = parser.predict(tests[i])

        for depend in sorted(dependencies[0]):
            d = parser.devectorize(tests[i])
            print(d[depend[0]], d[depend[1]])

    input_sentence = parser.read_str(str(input()))

    dependencies = parser.predict(input_sentence)

    for depend in sorted(dependencies[0]):
            d = parser.devectorize(input_sentence)
            print(d[depend[0]], d[depend[1]])