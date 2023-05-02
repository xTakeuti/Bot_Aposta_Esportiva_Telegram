import requests
import pandas as pd
import numpy as np
import re
from time import sleep

data = requests.get('https://www.totalcorner.com/match/today')

df = pd.read_html(data.text)[0]

df.dropna(axis=1, how='all', inplace=True)

df.dropna(axis=0, how='any', inplace=True)

df.drop(columns=['Handicap', 'Goal Line', 'Analysis', 'Time'], inplace=True)

df.rename(columns={'Unnamed: 3': 'Cronometro'}, inplace=True)

df['Cronometro'] = df['Cronometro'].apply(lambda a: 45 if a == 'Half' else a).astype('int64')

df['Corner'] = df['Corner'].apply(lambda a: re.findall(r'\d{1,} - \d{1,}', a))

list(map(int, df['Corner'].iloc[0][0].split('-')))

df['Corner'] = df['Corner'].apply(lambda a: list(map(int, a[0].split(' - '))))

df['Dangerous Attack'] = df['Dangerous Attack'].apply(lambda a: re.findall(r'\d{1,} - \d{1,}', a))

df['Shots'] = df['Shots'].apply(lambda a: re.findall(r'\d{1,} - \d{1,}', a))

df['Dangerous Attack'] = df['Dangerous Attack'].apply(lambda a: a if a != [] else np.nan)
df['Corner'] = df['Corner'].apply(lambda a: a if a != [] else np.nan)
df['Shots'] = df['Shots'].apply(lambda a: a if a != [] else np.nan)

df.dropna(axis=0, how='any', inplace=True)

df['Shots'] = df['Shots'].apply(lambda a: list(map(int, a[0].split(' - '))))
df['Dangerous Attack'] = df['Dangerous Attack'].apply(lambda a: list(map(int, a[0].split(' - '))))


def enviar_mensagens(msg):
    bot_token = ''#insira aqui o token id!!!
    chat_id = ''#Insira aqui seu chat id!!!
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}'
    requests.post(url)


mensagens_enviadas = []

for i in range(len(df)):
    j = df.iloc[i]
    tempo = j['Cronometro']

    appm_casa = round(j['Dangerous Attack'][0] / tempo, 1)
    appm_fora = round(j['Dangerous Attack'][1] / tempo, 1)

    cg_casa = j['Corner'][0] + j['Shots'][0]
    cg_fora = j['Corner'][1] + j['Shots'][1]

    condicao_casa = appm_casa >= 1 and cg_casa >= 15
    condicao_fora = appm_fora >= 1 and cg_fora >= 15

    t1 = 30 < tempo < 41
    t2 = 79 < tempo < 86

    if (condicao_casa or condicao_fora) and t1 or t2:
        if t1:
            t = 't1'
        else:
            t = 't2'

        home = re.sub(r'^\d{1}', '', j['Home'])
        away = re.sub(r'\d{1}$', '', j['Away'])

        if f'{home} x {away} _ {t}' not in mensagens_enviadas:
            msg = (f'''Liga:{j["League"]}
jogo: {home} x {away}
placar: {j["Score"]}     
appm: {appm_casa} - {appm_fora}
CG: {cg_casa} - {cg_fora}     
''')
            enviar_mensagens(msg)
            mensagens_enviadas.append(f'{home} x {away} {t}')
            sleep(2)
