Top! Bora completar o **README** do teu projeto **Email Classifier + AutoReply** já pensando no que você montou (FastAPI no backend + Vue no frontend).

Aqui vai uma versão **completa e organizada**:

---

```markdown
# 📧 Email Classifier + AutoReply

Uma aplicação simples para **classificar emails** como **Produtivo** ou **Improdutivo** e gerar **respostas automáticas**.  

---

## 🚀 Tecnologias

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/), Python
- **Frontend:** [Vue 3](https://vuejs.org/)
- **PDF/Texto:** [pypdf](https://pypi.org/project/pypdf/)
- **Opcional (IA):** OpenAI GPT para classificação avançada
- **Armazenamento:** JSON local

---

## 📌 Funcionalidades

✅ Classificação de texto manual ou arquivos **.txt/.pdf**  
✅ Resposta automática baseada na categoria  
✅ Salvamento local dos emails em arquivo JSON  
✅ Filtro de emails por categoria  
✅ Interface minimalista em Vue 3  

---

## 📂 Estrutura do Projeto

```

backend/       # Código Python + FastAPI
frontend/      # Código Vue 3 (index.html, App.vue etc.)
data/          # Armazena emails classificados (JSON)

````

---

## ⚡ Como rodar

### 1. Backend (FastAPI + Python)

1. Vá até a pasta do backend:
   ```bash
   cd backend
````

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install fastapi uvicorn pydantic python-dotenv pypdf
   ```

4. Inicie o servidor:

   ```bash
   uvicorn main:app --reload
   ```

   🔗 Acesse em: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   📄 Documentação automática: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2. Frontend (Vue 3)

1. Vá até a pasta do frontend:

   ```bash
   cd frontend
   ```

2. Instale as dependências:

   ```bash
   npm install
   ```

3. Rode o servidor de desenvolvimento:

   ```bash
   npm run dev
   ```

   🔗 Frontend disponível em: [http://localhost:5173](http://localhost:5173)

---

### 3. Integração Frontend + Backend

O frontend precisa chamar o backend pelo endpoint da API.
Normalmente isso é configurado em um **arquivo `.env`** ou direto no código Vue.

Exemplo de configuração (`frontend/.env`):

```env
VITE_API_URL=http://127.0.0.1:8000
```

No código Vue, você pode usar:

```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

---

## 📝 Exemplo de uso da API

### Classificar texto

```http
POST /classify
Content-Type: application/json

{
  "email": "Reunião amanhã às 10h sobre o projeto"
}
```

Resposta:

```json
{
  "categoria": "Produtivo",
  "resposta": "Confirmado. Estarei presente na reunião."
}
```

---

## 📌 Próximos passos

* [ ] Adicionar suporte a IA com OpenAI GPT
* [ ] Criar persistência em banco de dados (SQLite/Postgres)
* [ ] Melhorar interface do frontend

---

## 👨‍💻 Autor

Feito por **Vitor Gamarano** 🚀
[GitHub](https://github.com/Vitor-S-G-C) | [Email](mailto:vitorgamarano1@gmail.com)

---


