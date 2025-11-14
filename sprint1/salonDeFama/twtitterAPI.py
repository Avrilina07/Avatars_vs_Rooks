"""
Módulo para publicar el Top 10 en Twitter usando Tweepy (v2)

Provee una función `post_top10(top_list, dry_run=False)` que publica los
puntajes como uno o varios tweets en hilo si es necesario.

Si Tweepy no está disponible o falla, el módulo hace fallback a imprimir
el mensaje en consola.
"""

import os
import sys

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except Exception as e:
    tweepy = None
    TWEEPY_AVAILABLE = False
    print(f"[Advertencia] Tweepy no está disponible: {e}", file=sys.stderr)

# Credenciales (puedes moverlas a variables de entorno si lo prefieres)
API_KEY = '6nxM9RRFr3YT8dfBpRAR7Mfzz'
API_SECRET_KEY = 'mBneWG7QzYvKckmCELEVw3dlvFtseNqDMMwRcXscyc9BFhb4Xs'
ACCESS_TOKEN = '1989343501222551553-opMHO3MpTK3ZRsmKt4jMh5YFggFLa1'
ACCESS_SECRET = 'dQ9rz4xKYwDX4EHpGeqadcmHWD9lLTnKH9MSY25aZ2IiD'


def _create_client():
    """Crea y retorna un cliente de Tweepy (o None si no está disponible)."""
    if tweepy is None:
        print("[Twitter] tweepy no disponible", file=sys.stderr)
        return None
    try:
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET_KEY,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        print("[Twitter] Cliente de Tweepy creado exitosamente", file=sys.stderr)
        return client
    except Exception as e:
        print(f"[Twitter] Error creando cliente de Tweepy: {e}", file=sys.stderr)
        return None


def _split_lines_to_tweets(lines, max_len=280):
    """Agrupa líneas en bloques que quepan en tweets de longitud `max_len`.

    Devuelve lista de strings (cada uno para un tweet).
    """
    tweets = []
    current = []
    for line in lines:
        cand = "\n".join(current + [line]) if current else line
        if len(cand) <= max_len:
            current.append(line)
        else:
            if current:
                tweets.append("\n".join(current))
            # If single line is longer than max_len, truncate it
            if len(line) > max_len:
                tweets.append(line[:max_len - 3] + "...")
                current = []
            else:
                current = [line]
    if current:
        tweets.append("\n".join(current))
    return tweets


def post_top10(top_list, dry_run=False):
    """Publica el top 10 en Twitter.

    Args:
        top_list: lista de tuplas (posicion, usuario, puntaje)
        dry_run: si True, no publica, solo imprime lo que publicaría

    Retorna: lista de ids de tweets publicados (vacío si dry_run o falla)
    """
    lines = ["Top 10 - Salon de la Fama:"]
    for pos, usuario, puntaje in top_list:
        lines.append(f"{pos}. {usuario} — {puntaje:.2f}")

    tweets = _split_lines_to_tweets(lines, max_len=280)

    # Allow overriding with environment variable TWITTER_DRY_RUN=1
    env_dry = os.environ.get('TWITTER_DRY_RUN')
    if env_dry in ('1', 'true', 'True'):
        dry_run = True
    
    print(f"[Twitter] dry_run={dry_run}, tweepy_available={TWEEPY_AVAILABLE}", file=sys.stderr)

    if dry_run:
        print("[Twitter] MODO DRY RUN ACTIVADO. Tweets que se publicarían:")
        for i, t in enumerate(tweets, 1):
            print(f"--- Tweet {i} ---\n{t}\n")
        return []
    
    if tweepy is None or not TWEEPY_AVAILABLE:
        print("[Twitter] tweepy no disponible. MODO SIMULACIÓN. Tweets que se publicarían:", file=sys.stderr)
        for i, t in enumerate(tweets, 1):
            print(f"--- Tweet {i} ---\n{t}\n")
        return []

    client = _create_client()
    if client is None:
        print("[Twitter] No se pudo crear el cliente de Twitter. Abortando publicación.", file=sys.stderr)
        return []

    posted_ids = []
    reply_to = None
    try:
        for i, t in enumerate(tweets, 1):
            try:
                print(f"[Twitter] Publicando tweet {i}/{len(tweets)}...", file=sys.stderr)
                if reply_to:
                    resp = client.create_tweet(text=t, in_reply_to_tweet_id=reply_to)
                else:
                    resp = client.create_tweet(text=t)
                
                tid = None
                try:
                    tid = resp.data.get('id') if resp and resp.data else None
                except Exception as extract_err:
                    print(f"[Twitter] Error extrayendo ID del tweet: {extract_err}", file=sys.stderr)
                    tid = None
                
                if tid:
                    print(f"[Twitter] ✓ Tweet {i} publicado. ID: {tid}", file=sys.stderr)
                    posted_ids.append(tid)
                    reply_to = tid
                else:
                    print(f"[Twitter] ⚠ Tweet {i} publicado pero no se pudo obtener el ID", file=sys.stderr)
            except Exception as tweet_err:
                print(f"[Twitter] Error publicando tweet {i}: {tweet_err}", file=sys.stderr)
    except Exception as e:
        print(f"[Twitter] Error general publicando tweets: {e}", file=sys.stderr)
    
    print(f"[Twitter] Total de tweets publicados: {len(posted_ids)}/{len(tweets)}", file=sys.stderr)
    return posted_ids
