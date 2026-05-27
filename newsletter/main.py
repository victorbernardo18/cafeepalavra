import os
import sys
import json
import time
import datetime
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Carrega variáveis do arquivo .env (se existir localmente)
load_dotenv()

# Definição do modelo de saída desejado do editor
class DevotionalContent(BaseModel):
    assunto: str = Field(..., description="Um assunto curto, amigável e inspirador para o e-mail (evite usar caixa alta). Ex: 'Um recomeço com coragem'")
    versiculo_texto: str = Field(..., description="O texto bíblico completo do versículo selecionado com sua referência no final. Ex: 'Não fui eu que ordenei? Seja forte e corajoso! Não se apavore nem desanime... (Josué 1:9)'")
    reflexao: str = Field(..., description="A reflexão teológica revisada e dividida em 2 a 3 parágrafos curtos, separados por quebras de linha.")
    acao_do_dia: str = Field(..., description="Uma ação prática curta, simples e concreta baseada na reflexão para o leitor aplicar hoje.")

def obter_data_extenso():
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    agora = datetime.datetime.now()
    return f"{agora.day} de {meses[agora.month]} de {agora.year}"

def get_audience_emails(api_key, audience_id):
    """
    Busca os contatos inscritos e ativos da audiência no Resend via API REST.
    """
    url = f"https://api.resend.com/audiences/{audience_id}/contacts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"Buscando contatos da audiência {audience_id}...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    emails = []
    for contact in data.get("data", []):
        if not contact.get("unsubscribed", False):
            emails.append(contact["email"])
            
    print(f"Total de contatos ativos encontrados: {len(emails)}")
    return emails

def main():
    # 1. Carregar e verificar chaves de ambiente
    openai_api_key = os.getenv("OPENAI_API_KEY")
    resend_api_key = os.getenv("RESEND_API_KEY")
    resend_audience_id = os.getenv("RESEND_AUDIENCE_ID")
    sender_email = os.getenv("SENDER_EMAIL")
    pix_key = os.getenv("PIX_KEY", "pix@cafeepalavra.com.br")
    site_url = os.getenv("SITE_URL", "https://cafeepalavra.com.br")
    test_email = os.getenv("TEST_EMAIL")

    if not openai_api_key:
        print("Erro: A variável OPENAI_API_KEY não foi configurada.")
        sys.exit(1)
        
    if not resend_api_key:
        print("Erro: A variável RESEND_API_KEY não foi configurada.")
        sys.exit(1)

    # 2. Carregar o tema do dia (usando caminho relativo ao próprio script)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temas_path = os.path.join(script_dir, "temas.json")
        with open(temas_path, "r", encoding="utf-8") as f:
            temas = json.load(f)
    except Exception as e:
        print(f"Erro ao ler temas.json: {e}")
        sys.exit(1)

    # 0 = Segunda, 1 = Terça... 6 = Domingo
    weekday = datetime.datetime.now().weekday()
    tema_hoje = next((t for t in temas if t["dia_semana"] == weekday), temas[0])
    
    print(f"Tema de hoje ({tema_hoje['dia_nome']}): {tema_hoje['tema']}")

    # 3. Inicializar LLM (GPT-4o-mini pelo baixo custo)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.7
    )

    # 4. Criar Agentes do CrewAI
    teologo = Agent(
        role="Teólogo e Conselheiro Espiritual",
        role_description="Teólogo e Conselheiro Espiritual com ampla vivência em aconselhamento familiar e pastoral.",
        goal="Escolher um versículo bíblico adequado e escrever uma reflexão teológica diária curta, acolhedora e inspiradora.",
        backstory=(
            "Você é um teólogo com ampla vivência em aconselhamento familiar e pastoral. "
            "Seu tom é sempre acolhedor, sábio e pautado por esperança, liberdade e responsabilidade pessoal. "
            "Você evita termos teológicos complexos, julgamento ou fatalismo, buscando aproximar o versículo da vida prática do leitor "
            "com a doçura e a clareza de uma conversa de café da manhã."
        ),
        llm=llm,
        verbose=True
    )

    editor = Agent(
        role="Editor e Redator de E-mail",
        role_description="Editor literário e copywriter especializado em newsletters diárias.",
        goal="Revisar e polir a reflexão do teólogo, definir um assunto cativante e de alta conversão para o e-mail, e criar a Ação Prática do Dia.",
        backstory=(
            "Você é um editor literário e copywriter especializado em newsletters diárias. "
            "Você garante que o conteúdo seja leve, acolhedor e formatado de forma que a leitura seja fluida e prazerosa em telas de celular. "
            "Você sabe como extrair uma aplicação prática extremamente direta para o dia de quem lê."
        ),
        llm=llm,
        verbose=True
    )

    # 5. Criar Tarefas
    reflexao_task = Task(
        description=(
            f"Com base no tema do dia: '{tema_hoje['tema']}' e diretriz editorial: '{tema_hoje['diretriz_editorial']}'.\n"
            f"Escolha um versículo inspirador e adequado (preferencialmente baseado em '{tema_hoje['versiculo_referencia']}' da tradução NVI ou similar).\n"
            "Escreva uma reflexão diária acolhedora de 2 a 3 parágrafos relacionando o versículo a desafios comuns do cotidiano."
        ),
        expected_output="Uma reflexão diária estruturada em parágrafos e o versículo bíblico de referência.",
        agent=teologo
    )

    format_task = Task(
        description=(
            "Revise e melhore a reflexão gerada pelo Teólogo para torná-la ainda mais acolhedora, limpa e cativante.\n"
            "Escreva um assunto (título) do e-mail curto e amigável.\n"
            "Crie a 'Ação Prática do Dia': um conselho ou atitude simples e direta que o leitor possa fazer hoje mesmo.\n"
            "Retorne a resposta estritamente estruturada de acordo com o modelo Pydantic fornecido."
        ),
        expected_output="O conteúdo do devocional estruturado em JSON contendo assunto, versiculo_texto, reflexao e acao_do_dia.",
        agent=editor,
        output_json=DevotionalContent
    )

    # 6. Executar a Crew
    crew = Crew(
        agents=[teologo, editor],
        tasks=[reflexao_task, format_task],
        verbose=True
    )

    print("Iniciando geração de conteúdo via CrewAI...")
    result = crew.kickoff()
    
    # 7. Parsear o resultado JSON de forma resiliente
    output_dict = None
    try:
        if hasattr(format_task.output, 'json_dict') and format_task.output.json_dict:
            output_dict = format_task.output.json_dict
        elif hasattr(result, 'json_dict') and result.json_dict:
            output_dict = result.json_dict
        else:
            raw_text = result.raw if hasattr(result, 'raw') else str(result)
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            output_dict = json.loads(raw_text)
    except Exception as e:
        print(f"Erro ao parsear saída em JSON: {e}. Usando fallback.")
        # Fallback se falhar no parse estruturado
        output_dict = {
            "assunto": f"Uma boa palavra para sua {tema_hoje['dia_nome']}",
            "versiculo_texto": f"Espera no Senhor, anima-te, e ele fortalecerá o teu coração. ({tema_hoje['versiculo_referencia']})",
            "reflexao": str(result),
            "acao_do_dia": "Dedique 5 minutos hoje para respirar, orar e agradecer pelas pequenas coisas."
        }

    # 8. Formatar parágrafos da reflexão para HTML
    reflexao_raw = output_dict.get("reflexao", "")
    reflexao_paragraphs = reflexao_raw.split("\n")
    reflexao_html = ""
    for p in reflexao_paragraphs:
        p_text = p.strip()
        if p_text:
            p_text = p_text.replace("\n", "<br>")
            reflexao_html += f'<p style="margin: 0 0 16px 0; text-align: justify;">{p_text}</p>'

    # 9. Montar o Link de Compartilhamento no WhatsApp
    share_text = f"Já garantiu sua leitura de amanhã? Convide alguém que precisa de uma boa palavra hoje: {site_url}"
    whatsapp_share_link = f"https://api.whatsapp.com/send?text={requests.utils.quote(share_text)}"

    # 10. Injetar conteúdo no HTML Template elegante
    data_extenso = obter_data_extenso()
    assunto_final = output_dict.get("assunto", "Café & Palavra")
    
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assunto_final}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f7f5f2; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; color: #2b1d0e;">
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f7f5f2; padding: 40px 10px;">
        <tr>
            <td align="center">
                <!-- Container principal -->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); border: 1px solid rgba(43, 29, 14, 0.05);">
                    
                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 40px 20px 40px; background-color: #ffffff;">
                            <span style="font-size: 32px; display: inline-block; margin-bottom: 10px;">☕</span>
                            <h1 style="margin: 0; font-family: Georgia, serif; font-size: 28px; font-weight: 700; color: #3e2712; letter-spacing: 0.5px;">Café & Palavra</h1>
                            <p style="margin: 5px 0 0 0; font-size: 13px; color: #8c7662; text-transform: uppercase; letter-spacing: 2px;">{data_extenso}</p>
                        </td>
                    </tr>

                    <!-- Linha divisória -->
                    <tr>
                        <td style="padding: 0 40px;">
                            <hr style="border: 0; border-top: 1px solid #efebe7; margin: 0;">
                        </td>
                    </tr>

                    <!-- Conteúdo Devocional -->
                    <tr>
                        <td style="padding: 40px;">
                            
                            <!-- Bloco do Versículo -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fbfaf8; border-left: 3px solid #d4a373; border-radius: 4px 12px 12px 4px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 20px 24px;">
                                        <p style="margin: 0; font-family: Georgia, serif; font-style: italic; font-size: 16px; line-height: 1.6; color: #4e3629;">
                                            "{output_dict.get('versiculo_texto')}"
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Reflexão -->
                            <div style="font-size: 16px; line-height: 1.7; color: #2b1d0e; font-weight: 350;">
                                {reflexao_html}
                            </div>

                            <!-- Espaçador -->
                            <div style="height: 30px;"></div>

                            <!-- Bloco da Ação do Dia -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #faf5ef; border: 1px dashed #d4a373; border-radius: 16px;">
                                <tr>
                                    <td style="padding: 24px;">
                                        <h3 style="margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #a06a38; font-weight: 700;">
                                            Ação Prática do Dia
                                        </h3>
                                        <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #2b1d0e;">
                                            {output_dict.get('acao_do_dia')}
                                        </p>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- Rodapé / Doações e Links -->
                    <tr>
                        <td style="padding: 40px; background-color: #faf9f6; border-top: 1px solid #efebe7; text-align: center;">
                            
                            <!-- Pix Box -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 25px;">
                                <tr>
                                    <td align="center">
                                        <p style="margin: 0 0 8px 0; font-size: 14px; color: #4e3629; font-weight: 600;">
                                            ❤️ Mantenha este projeto ativo
                                        </p>
                                        <p style="margin: 0 0 16px 0; font-size: 12px; line-height: 1.5; color: #8c7662; max-width: 340px;">
                                            O Café & Palavra é gratuito. Se as reflexões têm feito bem ao seu dia, apoie a manutenção dos nossos servidores com qualquer valor via PIX.
                                        </p>
                                        <div style="display: inline-block; background-color: #ffffff; padding: 10px 18px; border-radius: 10px; border: 1px solid #e1dbd5; font-family: monospace; font-size: 13px; color: #3e2712; font-weight: bold; letter-spacing: 0.5px;">
                                            Chave PIX: {pix_key}
                                        </div>
                                    </td>
                                </tr>
                            </table>

                            <!-- Divisor sutil -->
                            <div style="height: 1px; background-color: #efebe7; margin: 25px 0;"></div>

                            <!-- Botão de Compartilhar -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 25px;">
                                <tr>
                                    <td align="center">
                                        <a href="{whatsapp_share_link}" target="_blank" style="display: inline-block; background-color: #25D366; color: #ffffff; text-decoration: none; font-size: 14px; font-weight: bold; padding: 12px 24px; border-radius: 10px; box-shadow: 0 2px 5px rgba(37, 211, 102, 0.2);">
                                            Compartilhar no WhatsApp
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Opt-out e notas legais -->
                            <p style="margin: 0; font-size: 11px; color: #a4907e; line-height: 1.5;">
                                Você recebeu este e-mail porque se inscreveu na nossa Landing Page.<br>
                                Se não deseja mais receber nossas mensagens diárias, <a href="http://{{{{{{unsubscribe_url}}}}}}" style="color: #a06a38; text-decoration: underline;">cancele a sua inscrição</a>.
                            </p>

                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    # 11. Definir lista de e-mails para envio
    recipients = []
    if test_email:
        print(f"Modo de teste ativado. Enviando apenas para: {test_email}")
        recipients = [test_email]
    else:
        if not resend_audience_id:
            print("Erro: A variável RESEND_AUDIENCE_ID é necessária para envio em lote (modo produção).")
            sys.exit(1)
        try:
            recipients = get_audience_emails(resend_api_key, resend_audience_id)
        except Exception as e:
            print(f"Falha ao buscar contatos da audiência no Resend: {e}")
            sys.exit(1)

    if not recipients:
        print("Nenhum destinatário ativo encontrado para envio.")
        return

    # 12. Executar disparos através da API do Resend
    import resend as resend_sdk
    resend_sdk.api_key = resend_api_key
    
    sucesso = 0
    falha = 0
    
    print(f"Iniciando disparos de e-mail com remetente: {sender_email}")
    for email in recipients:
        try:
            print(f"Enviando para {email}...")
            resend_sdk.Emails.send({
                "from": sender_email,
                "to": email,
                "subject": assunto_final,
                "html": html_template
            })
            sucesso += 1
            # Atraso para respeitar limites da conta grátis
            time.sleep(0.5)
        except Exception as err:
            print(f"Erro ao enviar para {email}: {err}")
            falha += 1

    print("\n=== RESUMO DOS DISPAROS ===")
    print(f"Sucesso: {sucesso}")
    print(f"Falha: {falha}")

if __name__ == "__main__":
    main()
