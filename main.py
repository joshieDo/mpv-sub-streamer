import subprocess, time, sys
from pyautogui import hotkey
from flask import Flask, render_template, Response
from flask_sock import Sock
from PIL import Image
import pyperclip


def get_clipboard():
    p = subprocess.Popen(
        ["xclip", "-selection", "clipboard", "-o"], stdout=subprocess.PIPE
    )
    p.wait()
    if p.returncode == 0:
        data = p.stdout.read()
        return data.decode()
    return "invalid"


def process_tokens(tks):
    doc = nlp(tks)
    for sent in doc.sents:
        for token in sent:
            return token.lemma_


try:
    from manga_ocr import MangaOcr

    mocr = MangaOcr("kha-white/manga-ocr-base", False)
except:
    print("Missing MangaOCR.")

try:
    import spacy

    nlp = spacy.load("ja_ginza_electra")
except:
    print("Missing spacy_ginza_electra")


app = Flask(__name__)
sock = Sock(app)
before = [""]


@sock.route("/subs")
def subs(ws):
    global before
    while True:

        try:
            clipped = get_clipboard()
            if clipped != before[0]:
                before.insert(0, clipped)

                if len(before) > 20:
                    before = before[:-1]

                ws.send("</br><hr>".join(before))
        except Exception as e:
            print(e)

        time.sleep(0.02)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sb")
def sb():
    hotkey("shift", "h")
    return Response(status=200)


@app.route("/b")
def b():
    hotkey("left")
    return Response(status=200)


@app.route("/pp")
def pp():
    hotkey("p")
    return Response(status=200)


@app.route("/f")
def f():
    hotkey("right")
    return Response(status=200)


@app.route("/sf")
def sf():
    hotkey("shift", "l")
    return Response(status=200)


@app.route("/anki")
def anki_media():
    hotkey("ctrl", "shift", "m")
    return Response(status=200)


@app.route("/clip")
def clip():
    res = mocr(Image.open("/tmp/kanji"))
    pyperclip.copy(res)

    lemma = process_tokens(res)

    try:
        from jamdict import Jamdict

        jam = Jamdict()
    except:
        print("Missing jamdict")

    word = jam.lookup(lemma)
    reading = word.entries[0].kana_forms[0]
    meaning = str(word.entries[0].senses[0]).split("(")[0]

    return f"{lemma} | {reading} | {meaning}"


if __name__ == "__main__":
    host, port = sys.argv[1].split(":")
    app.run(host, port=port)
