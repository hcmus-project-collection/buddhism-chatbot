
# ✅ Plan for Eastern Religion RAG Chatbot

## ✅ Stage 1: Data Preparation
- ✅ Convert XML to sentence-level JSONL format
  - Each line = 1 `<STC>` with NER and metadata
- ✅ (Optional) Preprocess `text` fields: remove noise, normalize punctuation, lowercase, etc.
- [ ] (Optional) Split into `train`, `test`, `dev` sets if needed (e.g., for eval)

---

## ✅ Stage 2: Embedding & Indexing

### 📦 Choose Embedding Model
- ✅ Choose multilingual embedding model:
  - `intfloat/multilingual-e5-base`
  - `vinai/sentence-transformers-vi-m2`
  - or custom Sentence-BERT model fine-tuned on Buddhist QA

### 📥 Vector Indexing
- ✅ Choose vector DB: `FAISS`, `Qdrant`, or `Chroma`
- ✅ Write script to:
  - Load JSONL
  - Embed each `text` field
  - Store vector + `meta` (title, id, entities) in DB

---

## ✅ Stage 3: Retrieval Module

- [ ] Implement `retrieve(query)` function:
  - ✅ Embed user question
  - ✅ Retrieve top-k similar STC segments
  - ✅ Return both text and metadata

---

## ✅ Stage 4: Generation Module (Chatbot)

### 🧠 Choose LLM Backend
- [ ] Use:
  - `mistralai/Mistral-7B-Instruct`
  - `Qwen1.5-1.8B-Chat`
  - or `GPT-4` (via API)

### 📜 Prompt Template
- [ ] Design context-aware prompt:
  ```text
  [Question]
  {user_input}

  [Relevant Texts]
  {retrieved_passages}

  [Instruction]
  Hãy trả lời câu hỏi dựa vào nội dung và theo tinh thần đạo lý của An Sĩ Toàn Thư.
  ```

---

## ✅ Stage 5: Backend + API

- [ ] Build backend using `FastAPI`
  - `/ask` endpoint: receives query, runs RAG, returns answer
  - `/health` endpoint for status
- [ ] Optionally expose `/search` for just retrieval (debug)

---

## ✅ Stage 6: Frontend Interface

- [ ] Create Streamlit or React chat interface
- [ ] Display:
  - Generated answer
  - Retrieved context
  - Citation (e.g. page ID, section ID, sentence ID)

---

## ✅ Stage 7: Evaluation & QA

- [ ] Build evaluation script with:
  - Manual examples
  - Metrics like BLEU / ROUGE / semantic similarity (if gold answers)
- [ ] Add unit tests for edge cases

---

## ✅ Stage 8: Deployment (Optional)

- [ ] Dockerize backend + model inference
- [ ] Deploy on:
  - Hugging Face Spaces
  - Render / Railway / VPS
- [ ] Add monitoring/logging

---

## ✨ Bonus Features

- [ ] Add fuzzy NER search: "Who is Đế Quân?" → match `PER` entities
- [ ] Support multi-turn conversation history
- [ ] Add translation layer for bilingual support (Vietnamese ↔ English)
