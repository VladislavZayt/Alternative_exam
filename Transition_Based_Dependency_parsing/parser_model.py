import torch
import torch.nn as nn
import torch.nn.functional as F

class ParserModel(nn.Module): # модель для предсказания перехода 
    def __init__(self, embeddings, n_features=36,
        hidden_size=200, n_classes=3, dropout_prob=0.5): 
        super(ParserModel, self).__init__()
        self.n_features = n_features
        self.n_classes = n_classes
        self.dropout_prob = dropout_prob
        self.embed_size = embeddings.shape[1]
        self.hidden_size = hidden_size
        self.embeddings = nn.Parameter(torch.tensor(embeddings))

        self.embed_to_hidden_weight = nn.Parameter(nn.init.xavier_uniform_(torch.empty(self.n_features*self.embed_size, self.hidden_size)))
        self.embed_to_hidden_bias = nn.Parameter(nn.init.uniform_(torch.empty(self.hidden_size)))

        self.dropout = nn.Dropout(p=self.dropout_prob)

        self.hidden_to_logits_weight = nn.Parameter(nn.init.xavier_uniform_(torch.empty(self.hidden_size, self.n_classes)))
        self.hidden_to_logits_bias = nn.Parameter(nn.init.uniform_(torch.empty(self.n_classes)))

    def embedding_lookup(self, w):
        x = torch.index_select(self.embeddings, 0, w.view(-1)).view(w.shape[0], -1)
        return x


    def forward(self, w):
        embed_output = self.embedding_lookup(w)
        first_layer_out = self.dropout(F.relu(torch.matmul(embed_output, self.embed_to_hidden_weight) + self.embed_to_hidden_bias))
        logits = torch.matmul(first_layer_out, self.hidden_to_logits_weight) + self.hidden_to_logits_bias
        return logits