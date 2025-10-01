import os
import re
import json
from io import BytesIO
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Form, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


try:
    from openai import OpenAI
except Exception:
    OpenAI = None

import pypdf

# --- Configurações ---
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

EMAILS_DIR = "emails"
os.makedirs(EMAILS_DIR, exist_ok=True)
os.makedirs(os.path.join(EMAILS_DIR, "produtivo"), exist_ok=True)
os.makedirs(os.path.join(EMAILS_DIR, "improdutivo"), exist_ok=True)

app = FastAPI(title="Email Classifier + AutoReply (FastAPI)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = None
if OpenAI and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        openai_client = None

# --- Modelos ---
class ClassifyResponse(BaseModel):
    categoria: str
    resposta_sugerida: str


STOP_WORDS = {
    "a", "o", "e", "é", "de", "do", "da", "em", "um", "uma", "para", "com",
    "por", "que", "se", "os", "as", "no", "na", "ao", "à", "às", "dos", "das",
    "este", "esta", "esse", "essa", "sou", "tenho", "temos", "foi", "foi", "ser",
    "são", "eu", "vc", "você"
}

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"https?://\S+", " ", text)  # remove urls
    text = re.sub(r"[^a-z0-9çãõáéíóúâêîôûà\s\n]", " ", text)
    tokens = [t for t in re.split(r"\s+", text) if t and t not in STOP_WORDS]
    return " ".join(tokens)

KEYWORDS_PRODUTIVO = [
    "solicit", "ajuda", "erro", "problema", "requis", "ticket", "urgente",
    "pedido", "venda", "contrato", "fatura", "pagamento", "backup", "status",
    "atualização", "atualizar", "suporte", "instalar", "configurar", "alterar",
    "consulta", "pergunta", "dúvida", "duvida", "config", "problema", "falha"
]

def local_classify(text: str) -> str:
    sample = preprocess_text(text)
    score = 0
    for kw in KEYWORDS_PRODUTIVO:
        if kw in sample:
            score += 1
    
    return "Produtivo" if score >= 1 else "Improdutivo"

def local_generate_reply(text: str, category: str) -> str:
    if category == "Produtivo":
        return (
            "Olá — recebi sua mensagem. "
            "Obrigado por reportar. Vamos analisar e em breve retornaremos com uma solução ou próximos passos. "
            "Se possível, envie mais detalhes (prints, passos para reproduzir, ambiente)."
        )
    else:
        return "Obrigado pela mensagem! Agradecemos seu contato — vamos registrar aqui."


def openai_classify_and_reply(text: str) -> ClassifyResponse:
    # Usa o cliente OpenAI (API moderna fazendo chat completions via client.chat.completions.create)
    if not openai_client:
        raise RuntimeError("OpenAI client não disponível/configurado.")

    prompt = f"""
Você é um assistente que classifica e-mails em duas categorias:
- Produtivo: requer ação ou resposta específica.
- Improdutivo: não necessita de ação imediata.

Classifique estritamente como "Produtivo" ou "Improdutivo" e gere uma resposta curta adequada ao e-mail.
Retorne apenas JSON no formato:
{{
  "categoria": "Produtivo ou Improdutivo",
  "resposta_sugerida": "<resposta curta>"
}}

EMAIL:
---
{text}
---
"""
   
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini" if hasattr(openai_client, "chat") else "gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = resp.choices[0].message.content
        # pode ser uma string JSON
        parsed = json.loads(content)
        categoria = parsed.get("categoria", "").strip()
        resposta = parsed.get("resposta_sugerida", "").strip()
        if not categoria:
            raise ValueError("Resposta do OpenAI sem categoria.")
        return ClassifyResponse(categoria=categoria, resposta_sugerida=resposta)
    except Exception as e:
        raise RuntimeError(f"Falha ao chamar OpenAI: {str(e)}") from e


def classify_and_reply(text: str) -> ClassifyResponse:
    if not text or len(text.strip()) < 3:
        raise ValueError("Texto muito curto para classificação.")
   
    if openai_client:
        try:
            return openai_classify_and_reply(text)
        except Exception:
            
            pass
    
    categoria = local_classify(text)
    resposta = local_generate_reply(text, categoria)
    return ClassifyResponse(categoria=categoria, resposta_sugerida=resposta)


def salvar_email(texto: str, categoria: str, metadata: Optional[dict] = None) -> str:
    catdir = os.path.join(EMAILS_DIR, categoria.lower())
    os.makedirs(catdir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"email_{timestamp}.json"
    filepath = os.path.join(catdir, filename)
    payload = {
        "texto": texto,
        "categoria": categoria,
        "criado_em": timestamp,
        "metadata": metadata or {}
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return filepath


@app.post("/api/classify_text", response_model=ClassifyResponse)
async def api_classify_text(email_content: str = Form(...)):
    try:
        result = classify_and_reply(email_content)
        salvar_email(email_content, result.categoria, {"source": "text_form"})
        return JSONResponse(content=result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/classify_file", response_model=ClassifyResponse)
async def api_classify_file(file: UploadFile = File(...)):
    if file.content_type not in ["text/plain", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Apenas .txt e .pdf são permitidos.")
    try:
        raw = await file.read()
        text = ""
        if file.content_type == "text/plain":
            text = raw.decode("utf-8", errors="ignore")
        else:  
            reader = pypdf.PdfReader(BytesIO(raw))
            pages = []
            for p in reader.pages:
                t = p.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Arquivo sem texto extraível.")
        result = classify_and_reply(text)
        salvar_email(text, result.categoria, {"source": "file", "filename": file.filename})
        return JSONResponse(content=result.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@app.get("/api/list_emails")
def api_list_emails(categoria: Optional[str] = Query(None, description="produtivo|improdutivo (opcional)")):
    emails = []
    cats = []
    if categoria:
        cats = [categoria.lower()]
    else:
        cats = [d for d in os.listdir(EMAILS_DIR) if os.path.isdir(os.path.join(EMAILS_DIR, d))]
    for c in cats:
        dpath = os.path.join(EMAILS_DIR, c)
        if not os.path.isdir(dpath):
            continue
        for fname in sorted(os.listdir(dpath), reverse=True):
            fpath = os.path.join(dpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_path"] = fpath
                    emails.append(data)
            except Exception:
                continue
    return {"emails": emails}

@app.get("/")
def read_root():
    return {"message": "API rodando. Use /api/classify_text, /api/classify_file, /api/list_emails"}
