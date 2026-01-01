from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
import torch.nn.functional as F

app = FastAPI()

# -------- LOAD MODEL --------
import os

MODEL_PATH = "model/tiny_chatbot.pt"

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Model file missing: model/tiny_chatbot.pt")

checkpoint = torch.load(MODEL_PATH, map_location="cpu")
model = checkpoint["model"]
word_to_idx = checkpoint["vocab"]
idx_to_word = {v: k for k, v in word_to_idx.items()}
model.eval()

EOS = word_to_idx["<eos>"]

# -------- HELPERS --------
def encode(text):
    return [word_to_idx.get(w, word_to_idx["<unk>"]) for w in text.lower().split()]

def decode(tokens):
    words = []
    for t in tokens:
        if t == EOS:
            break
        words.append(idx_to_word.get(t, ""))
    return " ".join(words)

def generate_once(tokens, temp):
    out = tokens[:]
    h = None

    for _ in range(32):
        x = torch.tensor([out[-20:]])
        with torch.no_grad():
            logits, h = model(x, h)

        probs = F.softmax(logits[0, -1] / temp, dim=0)
        nxt = torch.multinomial(probs, 1).item()
        if nxt == EOS:
            break
        out.append(nxt)

    return out

def score(tokens):
    return len(tokens) - (len(tokens) - len(set(tokens))) * 1.8

def best_response(base):
    options = []
    for t in (0.6, 0.7, 0.8, 0.9):
        gen = generate_once(base, t)
        options.append((score(gen), gen))
    return max(options, key=lambda x: x[0])[1]

# -------- API --------
class Chat(BaseModel):
    message: str

@app.post("/chat")
def chat(data: Chat):
    base = encode(f"<user> {data.message} <bot>")
    out = best_response(base)
    return {"reply": decode(out)}

# -------- FRONTEND --------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")
