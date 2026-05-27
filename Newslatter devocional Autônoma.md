# PRD: Newsletter Devocional Autônoma (Projeto "Café & Palavra")

## 1. Visão Executiva
Um sistema de newsletter diária 100% autônomo, orquestrado por agentes de IA (CrewAI). O produto entrega reflexões bíblicas curtas diretamente no e-mail, monetizadas exclusivamente via doações (PIX). A captação de usuários ocorre através de uma Landing Page ultra-rápida, alimentada por um *Viral Loop* via WhatsApp. O foco operacional é custo zero e intervenção humana restrita ao suporte e manutenção básica.

## 2. Análise Estratégica e Validação da Stack (Menor Custo)
A arquitetura foi submetida a um teste de estresse financeiro. A stack escolhida representa o custo mínimo viável (próximo a zero) no cenário tecnológico atual, sem sacrificar a estabilidade.

*   **Validação do Custo Zero:** Ferramentas tradicionais de e-mail marketing (Mailchimp, ActiveCampaign) ou automação (Make) cobram assinaturas mensais que corroeriam as doações iniciais. Ao descentralizar a lógica para o GitHub Actions e o envio para o Resend, o custo fixo mensal cai para **US$ 0,00**.
*   **O Único Custo Variável:** Consumo de tokens da API da OpenAI (GPT-4o-mini). Para textos curtos de 3 parágrafos diários, o custo será de centavos de dólar ao longo do mês.
*   **O Custo Anual Obrigatório:** O registro do domínio (ex: `.com.br` por ~R$ 40/ano), essencial para a entregabilidade.
*   **Contraponto Construtivo:** Esta stack é barata, mas requer que o domínio seja "aquecido". Nos primeiros 15 dias, a taxa de entrega no Gmail pode oscilar até que os algoritmos confiem no seu remetente. Não inicie o Viral Loop em massa antes de testar a entrega com pequenos grupos.

## 3. Especificações do Produto e Linha Editorial
A IA operará sob limites editoriais estritos, projetados para gerar um sentimento de pertencimento e leveza.

*   **Tom de Voz:** Acolhedor, conselheiro e direto.
*   **Pilares de Conteúdo:** As reflexões devem invariavelmente reforçar princípios de **liberdade, valorização da família e otimismo** diante dos desafios diários. O conteúdo afasta-se de fatalismos e foca na responsabilidade pessoal com esperança.
*   **Formato de Saída (E-mail):**
    1.  **Versículo-chave** (Tradução NVI ou similar).
    2.  **Reflexão** (Máximo de 3 parágrafos).
    3.  **Ação do Dia** (Aplicação prática).
    4.  **Rodapé Funcional** (Link PIX + CTA de Compartilhamento).

## 4. Arquitetura Técnica Consolidada

A infraestrutura foi dividida em três pilares autônomos. A construção da Landing Page (LP) tira proveito da fluidez da geração de código por IA (Lovable), eliminando a necessidade de construtores pesados como WordPress.

| Pilar | Componente Técnico | Função e Justificativa de Custo |
| :--- | :--- | :--- |
| **Frontend (LP)** | Lovable + Cloudflare Pages | LP gerada via prompt e hospedada no Cloudflare (Plano Gratuito). Tempos de carregamento ultrarrápidos, essenciais para tráfego mobile. |
| **Cérebro (Lógica)** | Python + CrewAI + GH Actions | O script "acorda" de graça todos os dias no servidor do GitHub, gera o texto com GPT-4o-mini e orquestra o disparo. |
| **Banco de Contatos** | Resend (Audience API) | A LP envia os e-mails capturados direto para os contatos do Resend. Elimina a necessidade de um banco de dados externo. Plano grátis até 3.000 contatos. |

## 5. Engenharia do Funil e Viral Loop
O atrito foi reduzido a zero. O usuário nunca encontra telas complexas.

*   **Fase 1: Captação (Landing Page):**
    *   Design de dobra única, focada no mobile.
    *   Promessa clara ("5 minutos de paz matinal") + Campo único (Apenas E-mail).
*   **Fase 2: O Gatilho Viral (Página de Obrigado):**
    *   Após inserir o e-mail, o usuário não é apenas avisado do sucesso. A página apresenta um botão direto para o WhatsApp com o texto: *"Já garantiu sua leitura de amanhã? Convide alguém que precisa de uma boa palavra hoje: [LINK_DA_LP]"*.
*   **Fase 3: O Loop Diário (No E-mail):**
    *   Todo e-mail gerado pelos agentes conterá o CTA de doação (Honestidade radical: "Mantenha o projeto vivo") e o botão de reenvio para grupos.

## 6. Métricas de Sucesso (KPIs)
Indicadores essenciais para monitoramento esporádico:

1.  **Taxa de Conversão da LP:** Visitantes únicos vs. e-mails capturados (Alvo: > 25%).
2.  **Taxa de Abertura (Resend):** Saúde do domínio e relevância do assunto (Alvo: > 35%).
3.  **Conversão de Doação:** Número de PIXs recebidos vs. usuários ativos semanais.
4.  **Taxa de Rejeição (Bounce Rate):** E-mails não entregues (Alvo: < 2%, para não ter a conta bloqueada).

## 7. Requisitos para Lançamento (MVP)
Checklist prático para colocar o sistema no ar de forma ágil:

- [ ] Comprar o domínio e configurar os registros DNS (SPF/DKIM) no Resend.
- [ ] Gerar o Frontend (LP + Página de Obrigado) utilizando o Lovable e realizar o deploy gratuito no Cloudflare Pages ou Vercel.
- [ ] Conectar o formulário da LP à API do Resend (Endpoint de Audience).
- [ ] Subir o repositório no GitHub com o `temas.json` e o `main.py`.
- [ ] Configurar as variáveis de ambiente (API Keys) nas *Secrets* do GitHub Actions e testar o primeiro disparo manual.