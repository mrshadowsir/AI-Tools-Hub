from pathlib import Path
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT=Path(__file__).resolve().parent.parent
APP_DIR=Path(__file__).resolve().parent
OLLAMA_URL="http://127.0.0.1:11434"

app=FastAPI(title="Open-Source AI Lab")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

class ChatRequest(BaseModel):
    runtime:str
    model:str
    prompt:str
    task:str="chat"
    temperature:float=0.7

def instruction(task):
    return {"chat":"Answer naturally and directly.","explain":"Explain clearly with useful examples.","summarize":"Summarize accurately and concisely.","rewrite":"Rewrite clearly while preserving meaning.","code":"Act as a coding assistant and provide practical correct code."}.get(task,"Answer directly.")

@app.get("/api/health")
def health(): return {"ok":True}

@app.get("/api/ollama/models")
def ollama_models():
    try:
        r=requests.get(f"{OLLAMA_URL}/api/tags",timeout=5);r.raise_for_status()
        return {"models":[{"name":m.get("name",""),"size":m.get("size",0)} for m in r.json().get("models",[])]}
    except requests.RequestException as e:
        raise HTTPException(503,f"Ollama unavailable: {e}")

def chat_ollama(model,prompt,task,temp):
    try:
        r=requests.post(f"{OLLAMA_URL}/api/chat",json={"model":model,"stream":False,"options":{"temperature":temp},"messages":[{"role":"system","content":instruction(task)},{"role":"user","content":prompt}]},timeout=300)
        r.raise_for_status()
        return r.json().get("message",{}).get("content","")
    except requests.RequestException as e:
        raise HTTPException(502,f"Ollama inference failed: {e}")

_hf_cache={}
def chat_hf(model_id,prompt,task,temp):
    try:
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
    except ImportError:
        raise HTTPException(501,"Hugging Face Local is optional. Run INSTALL_HF_LOCAL.bat first.")
    if model_id not in _hf_cache:
        try:
            tok=AutoTokenizer.from_pretrained(model_id)
            kwargs={}
            if torch.cuda.is_available(): kwargs={"torch_dtype":torch.float16,"device_map":"auto"}
            mdl=AutoModelForCausalLM.from_pretrained(model_id,**kwargs)
            if not torch.cuda.is_available(): mdl.to("cpu")
            _hf_cache[model_id]=(tok,mdl)
        except Exception as e:
            raise HTTPException(400,f"Could not load model '{model_id}': {e}")
    tok,mdl=_hf_cache[model_id]
    text=f"System: {instruction(task)}\nUser: {prompt}\nAssistant:"
    try:
        inp=tok(text,return_tensors="pt")
        if torch.cuda.is_available(): inp={k:v.to(mdl.device) for k,v in inp.items()}
        out=mdl.generate(**inp,max_new_tokens=512,do_sample=temp>0,temperature=max(temp,0.01),pad_token_id=tok.eos_token_id)
        return tok.decode(out[0],skip_special_tokens=True).split("Assistant:",1)[-1].strip()
    except Exception as e:
        raise HTTPException(500,f"Local inference failed: {e}")

@app.post("/api/chat")
def chat(req:ChatRequest):
    if req.runtime=="ollama": return {"response":chat_ollama(req.model,req.prompt,req.task,req.temperature)}
    if req.runtime=="huggingface": return {"response":chat_hf(req.model,req.prompt,req.task,req.temperature)}
    raise HTTPException(400,"Unknown runtime.")

app.mount("/",StaticFiles(directory=str(APP_DIR),html=True),name="static")