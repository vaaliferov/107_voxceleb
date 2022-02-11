import torch
import torchaudio
import speechbrain

import numpy as np
import pandas as pd
import sklearn.metrics

import telegram.ext
from secret import *

params = {'source': 'speechbrain/spkrec-ecapa-voxceleb', 'run_opts': {'device': 'cpu'}}
ecapa = speechbrain.pretrained.EncoderClassifier.from_hparams(**params)
vox_df, vox_embs = pd.read_csv('vox.csv'), np.load('ecapa_vox.npy')
vox_df['start'] = vox_df['start'].round(0).astype(int).astype(str)

def handle_voice(update, context):
    
    user = update.message.from_user
    file_id = update.message.voice['file_id']
    context.bot.getFile(file_id).download('in.ogg')
    audio, sr = torchaudio.load('in.ogg')
    resample = torchaudio.transforms.Resample(sr, 16000)
    audio = resample(audio[:, :4 * sr]).to('cpu')
    in_emb = ecapa.encode_batch(audio)[0].detach().numpy()
    vox_df['sim'] = sklearn.metrics.pairwise.cosine_similarity(in_emb, vox_embs)[0]
    df = vox_df.sort_values(by='sim', ascending=False).groupby('id', sort=False).first()[:10]
    result = '\n'.join(df['name'] + '\nhttps://youtu.be/' + df['video'] + '?t=' + df['start'])
    context.bot.send_message(update.message.chat_id, result, disable_web_page_preview=True)
    
    if user['id'] != TG_BOT_OWNER_ID:
        msg = f"@{user['username']} {user['id']}"
        context.bot.send_message(TG_BOT_OWNER_ID, msg)
        context.bot.send_voice(TG_BOT_OWNER_ID, file_id)
        context.bot.send_message(TG_BOT_OWNER_ID, result, disable_web_page_preview=True)

h = telegram.ext.MessageHandler
f = telegram.ext.Filters.voice 
u = telegram.ext.Updater(TG_BOT_TOKEN)
u.dispatcher.add_handler(h(f, handle_voice))
u.start_polling(); u.idle()