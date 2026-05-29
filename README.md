# ☕ Café & Palavra — Newsletter Devocional Autônoma

Sistema completo de newsletter diária devocional, 100% autônomo e com custo de infraestrutura zero. A IA gera e envia reflexões bíblicas todos os dias automaticamente.

**Site:** [cafeepalavra.com](https://cafeepalavra.com)

---

## 🏗️ Arquitetura

| Pilar | Tecnologia | Função |
|---|---|---|
| **Frontend** | Cloudflare Pages | Landing page + formulário de inscrição |
| **API de inscrição** | Cloudflare Functions (`/api/subscribe`) | Recebe o email e cadastra no Resend de forma segura |
| **Geração de conteúdo** | Python + CrewAI + GPT-4o-mini | Agentes de IA geram o devocional diário |
| **Envio de email** | Resend Batch API | Dispara para todos os inscritos em lotes de 100 |
| **Automação** | GitHub Actions | Executa o script todo dia às 06:00 (horário de Brasília) |

---

## ⚙️ Variáveis de Ambiente

### GitHub Actions Secrets
Configure em: **Settings → Secrets and variables → Actions**

| Secret | Descrição |
|---|---|
| `OPENAI_API_KEY` | Chave da OpenAI (GPT-4o-mini) |
| `RESEND_API_KEY` | Chave da API do Resend (permissão Full Access) |
| `RESEND_AUDIENCE_ID` | ID da audiência no Resend |
| `SENDER_EMAIL` | Email remetente verificado no Resend |
| `PIX_KEY` | Chave PIX para doações |
| `SITE_URL` | URL do site (https://cafeepalavra.com) |
| `TEST_EMAIL` | *(opcional)* Email para testes — remove para envio em produção |

### Cloudflare Pages — Environment Variables
Configure via API ou painel em: **Workers & Pages → cafeepalavra → Settings**

| Variável | Descrição |
|---|---|
| `RESEND_API_KEY` | Chave do Resend com permissão Full Access |
| `RESEND_AUDIENCE_ID` | ID da audiência no Resend |

---

## 📧 Como o Email é Gerado

1. GitHub Actions dispara o script às **09:00 UTC (06:00 Brasília)**
2. O agente **Teólogo** recebe o tema do dia (`newsletter/temas.json`) e escreve versículo + reflexão
3. O agente **Editor** revisa, melhora e define o assunto do email
4. O script monta o HTML e envia via **Resend Batch** para todos os inscritos
5. O botão de WhatsApp no email compartilha o devocional completo + link de inscrição

---

## 🧪 Teste Local

1. Instale as dependências com Python 3.13:
   ```
   py -3.13 -m pip install -r newsletter/requirements.txt
   ```

2. Crie o arquivo `newsletter/.env` com suas chaves:
   ```env
   OPENAI_API_KEY=sua_chave
   RESEND_API_KEY=sua_chave
   RESEND_AUDIENCE_ID=seu_id
   SENDER_EMAIL=devocional@cafeepalavra.com
   PIX_KEY=sua_chave_pix
   SITE_URL=https://cafeepalavra.com
   TEST_EMAIL=seu_email_pessoal
   ```

3. Execute:
   ```
   cd newsletter
   py -3.13 main.py
   ```

> Com `TEST_EMAIL` configurado, o email vai apenas para esse endereço — não para a lista de inscritos.

---

## 📊 KPIs para Monitorar

| Métrica | Alvo |
|---|---|
| Taxa de conversão da LP | > 25% |
| Taxa de abertura dos emails | > 35% |
| Bounce rate | < 2% |
| Conversão de doação (PIX) | Monitorar semanalmente |

---

## 🔒 Segurança

- Nenhuma chave de API está no código-fonte
- O arquivo `newsletter/.env` está protegido pelo `.gitignore`
- A `RESEND_API_KEY` nunca é exposta ao frontend — a Cloudflare Function age como proxy seguro
- As chaves de produção ficam exclusivamente nos Secrets do GitHub e nas variáveis do Cloudflare

---

## 📁 Estrutura do Projeto

```
├── index.html                  # Landing page
├── styles.css                  # Estilos
├── app.js                      # Lógica do formulário
├── functions/
│   └── api/
│       └── subscribe.js        # Cloudflare Function — API de inscrição
├── newsletter/
│   ├── main.py                 # Script principal — geração e envio
│   ├── temas.json              # Pauta editorial por dia da semana
│   ├── requirements.txt        # Dependências Python
│   └── .env                    # Chaves locais (não commitado)
└── .github/
    └── workflows/
        └── daily_newsletter.yml # Agendamento GitHub Actions
```
