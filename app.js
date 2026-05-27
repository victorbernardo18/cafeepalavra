document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('subscribe-form');
    const emailInput = document.getElementById('email');
    const submitBtn = document.getElementById('btn-submit');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    const errorMsg = document.getElementById('error-message');
    
    const subscriptionState = document.getElementById('subscription-state');
    const thankyouState = document.getElementById('thankyou-state');
    const whatsappBtn = document.getElementById('whatsapp-share-btn');

    // Validação de E-mail
    function isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Exibe mensagem de erro
    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.add('visible');
        emailInput.classList.add('invalid');
    }

    // Esconde mensagem de erro
    function clearError() {
        errorMsg.textContent = '';
        errorMsg.classList.remove('visible');
        emailInput.classList.remove('invalid');
    }

    // Limpa erro ao digitar
    emailInput.addEventListener('input', clearError);

    // Manipulação do Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        
        if (!email) {
            showError('Por favor, insira o seu e-mail.');
            return;
        }
        
        if (!isValidEmail(email)) {
            showError('Por favor, insira um e-mail válido.');
            return;
        }

        // Estado de Carregamento
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');
        clearError();

        try {
            const response = await fetch('/api/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                // Transição suave para o Estado de Obrigado
                subscriptionState.classList.remove('active');
                
                setTimeout(() => {
                    subscriptionState.classList.add('hidden');
                    thankyouState.classList.remove('hidden');
                    
                    // Configura o link dinâmico de compartilhamento do WhatsApp
                    const siteUrl = window.location.origin;
                    const shareText = `Já garantiu sua leitura de amanhã? Convide alguém que precisa de uma boa palavra hoje: ${siteUrl}`;
                    whatsappBtn.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`;
                    
                    // Ativa a animação de entrada do sucesso
                    setTimeout(() => {
                        thankyouState.classList.add('active');
                    }, 50);
                }, 500);

            } else {
                // Erro retornado pela API
                const errorDetail = data.error || 'Não foi possível concluir a inscrição. Tente novamente.';
                showError(errorDetail);
                resetButton();
            }

        } catch (error) {
            // Erro de rede ou outro problema de conexão
            console.error('Subscription error:', error);
            showError('Erro de conexão. Verifique sua internet e tente novamente.');
            resetButton();
        }
    });

    function resetButton() {
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
});
