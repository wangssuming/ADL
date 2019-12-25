import re
import torch
torch.cuda.manual_seed_all(9487)

class Embedding:
    """
    Args:
        embedding_path (str): Path where embedding are loaded from (text file).
        words (None or list): If not None, only load embedding of the words in
            the list.
        oov_as_unk (bool): If argument `words` are provided, whether or not
            treat words in `words` but not in embedding file as `<unk>`. If
            true, OOV will be mapped to the index of `<unk>`. Otherwise,
            embedding of those OOV will be randomly initialize and their
            indices will be after non-OOV.
        lower (bool): Whether or not lower the words.
        rand_seed (int): Random seed for embedding initialization.
    """

    def __init__(self, embedding_path,
                 words=None, oov_as_unk=True, lower=True, rand_seed=524):
#        print(words)
        self.word_dict = {}
        self.vectors = None
        self.lower = lower
        self.extend(embedding_path, words, oov_as_unk)
        torch.manual_seed(rand_seed)

        if '</s>' not in self.word_dict:
            self.add(
                '</s>', torch.zeros(self.get_dim())
            )
        if '<unk>' not in self.word_dict:
            self.add('<unk>')

    def to_index(self, word):
        """
        word (str)

        Return:
             index of the word. If the word is not in `words` and not in the
             embedding file, then index of `<unk>` will be returned.
        """
#        print(self.word_dict)
        if self.lower:
            word = word.lower()

        if word not in self.word_dict:
            return self.word_dict['<unk>']
        else:
            return self.word_dict[word]

    def get_dim(self):
        return self.vectors.shape[1]

    def get_vocabulary_size(self):
        return self.vectors.shape[0]

    def add(self, word, vector=None):
        if self.lower:
            word = word.lower()

        if vector is not None:
            vector = vector.view(1, -1)
        else:
            vector = torch.empty(1, self.get_dim())
            torch.nn.init.uniform_(vector)
        self.vectors = torch.cat([self.vectors, vector], 0)
        self.word_dict[word] = len(self.word_dict)

    def extend(self, embedding_path, words, oov_as_unk=True):
        self._load_embedding(embedding_path, words)

        if words is not None and not oov_as_unk:
            # initialize word vector for OOV
            for word in words:
                if self.lower:
                    word = word.lower()

                if word not in self.word_dict:
                    self.word_dict[word] = len(self.word_dict)

            oov_vectors = torch.nn.init.uniform_(
                torch.empty(len(self.word_dict) - self.vectors.shape[0],
                            self.vectors.shape[1]))

            self.vectors = torch.cat([self.vectors, oov_vectors], 0)

    def _load_embedding(self, embedding_path, words):
        print(words)
        if words is not None:
            words = set(words)

        vectors = []
        with open(embedding_path, encoding="utf8") as fp:

            row1 = fp.readline()
            # if the first row is not header
            if not re.match('^[0-9]+ [0-9]+$', row1):
                # seek to 0
                fp.seek(0)
            # otherwise ignore the header

            for i, line in enumerate(fp):
                cols = line.rstrip().split(' ')
                word = cols[0]

                # skip word not in words if words are provided
                if words is not None and word not in words:
                    continue
                elif word not in self.word_dict:
                    self.word_dict[word] = len(self.word_dict)
                    vectors.append([float(v) for v in cols[1:]])
#        w2v = Word2Vec.load(embedding_path)
#
#        # Scan each word in the w2v model.
#        for word in w2v.wv.vocab:
#            # skip word not in words if words are provided
#            if words is not None and word not in words:
#                continue
#            elif word not in self.word_dict:
#                self.word_dict[word] = len(self.word_dict)
#                vectors.append(w2v.wv[word])

#        from gensim.models import Word2Vec
#        import multiprocessing
#        cpus = multiprocessing.cpu_count()
#        word2vec_dict = {}
#        w2v_model = []
#        embedding_dim = 64
#        window_ = 1
#        min_count_ = 0
#        sample_ = 1e-1
#        iter_ = 10
#        w2v_model = Word2Vec(words, size=embedding_dim, window=window_, min_count=min_count_,sample=sample_,iter=iter_,  workers=cpus/2, seed=0)
##        text_weights = w2v_model.wv.syn0 
##        vocab = dict([(k, v.index) for k,v in w2v_model.wv.vocab.items()])  
#        vocab_list = [k for k,v in w2v_model.wv.vocab.items()]
##        print(vocab_list)
#        word2vec_dict = dict([(k, w2v_model.wv[k]) for k in vocab_list])
#        for  i in range(len(word2vec_dict)):
#            cols = word2vec_dict.get(vocab_list[i])
#            self.word_dict[vocab_list[i]] = len(self.word_dict)
#            vectors.append([float(v) for v in cols])
##
##        
#        print(len(vocab_list))
#        print(len(word2vec_dict))
        vectors = torch.tensor(vectors)
#        print(vectors)
        if self.vectors is not None:
            self.vectors = torch.cat([self.vectors, vectors], dim=0)
        else:
            self.vectors = vectors
