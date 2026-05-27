# ☕ Café & Palavra - Projeto Newsletter Devocional Autônoma

Este projeto implementa uma infraestrutura completa de newsletter diária devocional que funciona 100% no modelo **custo zero** de infraestrutura. 

---

## 🛠️ Arquitetura do Sistema

O sistema é dividido em três partes principais totalmente independentes e serverless:
1. **Frontend (Landing Page)**: Captura de e-mails, hospedada de forma gratuita e ultrarrápida no **Cloudflare Pages**.
2. **Proxy de Inscrição (Cloudflare Function)**: Um endpoint serverless seguro (`/api/subscribe`) que se comunica com o Resend sem expor sua chave de API para o navegador.
3. **Cérebro de Envio (Python + CrewAI + GitHub Actions)**: Um script que acorda todas as manhãs no GitHub Actions, gera a reflexão diária de forma inteligente usando agentes de IA (CrewAI + GPT-4o-mini), monta um e-mail elegante e o envia para a sua audiência cadastrada no **Resend**.

---

## 🚀 Guia de Implantação Passo a Passo

### Passo 1: Configurar a Conta do Resend (E-mails e Contatos)
1. Crie uma conta gratuita em [resend.com](https://resend.com).
2. Vá em **Audiences** (Audiências), crie uma nova audiência com o nome `Café & Palavra` (ou o de sua preferência) e copie o **Audience ID** gerado.
3. Vá em **API Keys**, crie uma nova chave com permissões completas de escrita e salve-a.
4. *(Recomendado para produção)* Em **Domains**, adicione seu domínio próprio (ex: `cafeepalavra.com.br`) e configure as chaves DNS (SPF/DKIM/DMARC) no seu registrador para garantir a entregabilidade dos e-mails.

### Passo 2: Publicar o Repositório no GitHub
Como o script é executado pelo GitHub Actions, você deve subir os arquivos deste projeto para um repositório seu no GitHub (pode ser privado).

1. Crie um repositório no GitHub.
2. Suba todos os arquivos desta pasta para a raiz do repositório:
   - `index.html`
   - `styles.css`
   - `app.js`
   - `temas.json`
   - `requirements.txt`
   - `main.py`
   - Pasta `functions/`
   - Pasta `.github/`

### Passo 3: Configurar os Segredos do GitHub (Secrets)
Para que o GitHub Actions consiga rodar o CrewAI e enviar e-mails via Resend, você deve adicionar os segredos de ambiente no repositório do GitHub:
1. Vá nas configurações do seu repositório no GitHub (**Settings** > **Secrets and variables** > **Actions**).
2. Adicione os seguintes **New repository secret**:
   - `OPENAI_API_KEY`: Sua chave de API da OpenAI (gerada na plataforma da OpenAI).
   - `RESEND_API_KEY`: Sua API Key do Resend.
   - `RESEND_AUDIENCE_ID`: O ID da audiência criada no Resend.
   - `SENDER_EMAIL`: O e-mail de remetente cadastrado/autorizado no Resend (ex: `devocional@cafeepalavra.com.br` ou `onboarding@resend.dev` caso utilize o domínio padrão de teste).
   - `PIX_KEY`: A chave PIX que será exibida no rodapé para receber doações.
   - `SITE_URL`: A URL final da sua Landing Page (gerada no Cloudflare Pages no Passo 4).

### Passo 4: Fazer o Deploy do Frontend no Cloudflare Pages
1. Crie ou acesse sua conta no [dash.cloudflare.com](https://dash.cloudflare.com).
2. Vá em **Workers & Pages** > **Create application** > **Pages** > **Connect to Git**.
3. Selecione o repositório deste projeto que você criou no GitHub.
4. Nas configurações de Build:
   - **Framework preset**: `None`
   - **Build command**: (Deixe em branco)
   - **Build output directory**: (Deixe em branco ou coloque `/` para indicar a raiz)
5. Clique em **Save and Deploy**. O Cloudflare criará a página e gerará um subdomínio `.pages.dev`.
6. Após a primeira compilação, vá nas configurações da sua página no painel do Cloudflare:
   - Vá em **Settings** > **Environment variables**.
   - Adicione as variáveis do lado de produção:
     - `RESEND_API_KEY`: Sua API Key do Resend.
     - `RESEND_AUDIENCE_ID`: O ID da audiência criada no Resend.
   - Clique em **Save** e faça um novo redeploy para que a Function do Cloudflare aplique as variáveis.

---

## 🧪 Testando o Envio Manualmente

Você pode fazer um disparo de teste antes de deixar o sistema rodando no automático:
1. Configure as variáveis acima localmente ou configure o repositório.
2. Se quiser simular localmente, crie um arquivo `.env` na raiz do projeto com os seguintes valores:
   ```env
   OPENAI_API_KEY=sua_chave_openai
   RESEND_API_KEY=sua_chave_resend
   RESEND_AUDIENCE_ID=seu_id_de_audiencia
   SENDER_EMAIL=seu_email_autorizado
   PIX_KEY=sua_chave_pix
   TEST_EMAIL=seu_email_pessoal_para_teste
   ```
3. Se a variável `TEST_EMAIL` estiver configurada, o script **não** enviará para toda a lista do Resend, apenas para o e-mail de teste indicado, permitindo que você valide o layout e a reflexão da IA com segurança.
