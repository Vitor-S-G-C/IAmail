# Email Classifier + AutoReply

Uma aplicação simples para classificar emails como **Produtivo** ou **Improdutivo** e gerar respostas automáticas.  

---

## Tecnologias

- **Backend:** FastAPI, Python
- **Frontend:** Vue 3
- **PDF/Texto:** pypdf
- **Optional AI:** OpenAI GPT para classificação avançada

---

## Funcionalidades

- Classificação de texto ou arquivo (.txt/.pdf)
- Resposta automática baseada na categoria
- Armazenamento local dos emails em JSON
- Filtro de emails por categoria
- Interface minimalista em Vue 3

---

## Como usar

1. Instale dependências:
```bash
pip install fastapi uvicorn pydantic python-dotenv pypdf
