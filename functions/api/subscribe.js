const CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
};

export async function onRequestOptions() {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
}

export async function onRequestPost(context) {
    try {
        const { request, env } = context;
        
        // 1. Verificar chaves de ambiente essenciais
        const apiKey = env.RESEND_API_KEY;
        const audienceId = env.RESEND_AUDIENCE_ID;
        
        if (!apiKey || !audienceId) {
            return new Response(
                JSON.stringify({ error: "Configuração do servidor incompleta. RESEND_API_KEY ou RESEND_AUDIENCE_ID ausentes." }),
                { status: 500, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
            );
        }

        // 2. Extrair dados do corpo da requisição
        const body = await request.json();
        const email = body.email ? body.email.trim() : "";

        // 3. Validação do e-mail no backend
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
            return new Response(
                JSON.stringify({ error: "Endereço de e-mail inválido." }),
                { 
                    status: 400, 
                    headers: { "Content-Type": "application/json" } 
                }
            );
        }

        // 4. Enviar requisição para a API do Resend (Audience Contact)
        const resendResponse = await fetch(`https://api.resend.com/audiences/${audienceId}/contacts`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                unsubscribed: false
            })
        });

        // Tenta ler o JSON de resposta do Resend de forma segura
        let resendData = {};
        try {
            resendData = await resendResponse.json();
        } catch (e) {
            console.warn("Could not parse Resend JSON response", e);
        }

        // 5. Tratar resposta do Resend
        if (resendResponse.ok) {
            return new Response(
                JSON.stringify({ message: "Inscrição realizada com sucesso." }),
                { status: 200, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
            );
        } else {
            let errorMessage = "Ocorreu um erro ao cadastrar seu e-mail. Tente novamente.";

            if (resendResponse.status === 409 || (resendData?.message?.toLowerCase().includes("already exists"))) {
                return new Response(
                    JSON.stringify({ error: "Este e-mail já está inscrito em nossa newsletter!" }),
                    { status: 400, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
                );
            }

            return new Response(
                JSON.stringify({ error: resendData.message || errorMessage }),
                { status: resendResponse.status, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
            );
        }

    } catch (err) {
        console.error("Internal Server Error in subscribe Pages Function:", err);
        return new Response(
            JSON.stringify({ error: "Erro interno no servidor ao tentar processar a inscrição." }),
            { status: 500, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
        );
    }
}
