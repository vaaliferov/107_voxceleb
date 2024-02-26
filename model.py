import torchaudio
import speechbrain

import numpy as np
import pandas as pd


def pairwise_cosine_similarity(a, b):
    norm_a = np.linalg.norm(a, axis=1)
    norm_b = np.linalg.norm(b, axis=1)
    return np.dot(a, b.T) / np.outer(norm_a, norm_b)


class Model:

    def __init__(self, df_path, embs_path):

        params = {
            'run_opts': {'device': 'cpu'},
            'source': 'speechbrain/spkrec-ecapa-voxceleb'
        }

        self.df, self.embs = pd.read_csv(df_path), np.load(embs_path)
        self.df['start'] = self.df['start'].round(0).astype(int).astype(str)
        self.model = speechbrain.pretrained.EncoderClassifier.from_hparams(**params)

    def predict(self, path, topn=10):

        df = self.df.copy()

        audio, sr = torchaudio.load(path)
        resample = torchaudio.transforms.Resample(sr, 16000)

        audio = resample(audio[:, :4 * sr]).to('cpu')
        in_emb = self.model.encode_batch(audio)[0].detach().numpy()

        df['sim'] = pairwise_cosine_similarity(in_emb, self.embs)[0]
        df = df.sort_values(by='sim', ascending=False).groupby('id', sort=False).first()[:topn]
        return '\n'.join(df['name'] + '\nhttps://youtu.be/' + df['video'] + '?t=' + df['start'])