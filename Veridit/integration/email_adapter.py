# integration/email_adapter.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAdapter:
    def __init__(self):
        # NOTA: Para um projeto real, essas credenciais devem vir de variáveis de ambiente (.env)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_remetente = "projeto.veridit@gmail.com" # Coloque um email do grupo aqui
        self.senha_app = "zbutrgdqvtlqnwfj" # Leia a dica abaixo sobre essa senha

    def enviar_confirmacao_pagamento(self, email_destino: str, pacote_nome: str, creditos: int):
        """Envia o e-mail de confirmação do REQ 07"""
        assunto = "Veridit - Confirmação de Pagamento Aprovado! 🎉"
        
        corpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Olá! Seu pagamento foi processado com sucesso.</h2>
                <p>Obrigado por adquirir o pacote <strong>{pacote_nome}</strong> no Veridit RISE Labs.</p>
                <p>Foram adicionados <strong>{creditos} créditos</strong> à sua conta.</p>
                <br>
                <p>Você já pode começar a capturar suas evidências digitais.</p>
                <p>Atenciosamente,<br>Equipe Veridit</p>
            </body>
        </html>
        """

        mensagem = MIMEMultipart()
        mensagem['From'] = self.email_remetente
        mensagem['To'] = email_destino
        mensagem['Subject'] = assunto
        mensagem.attach(MIMEText(corpo_html, 'html'))

        try:
            print(f"📧 Tentando enviar e-mail de confirmação para {email_destino}...")
            # Conecta ao servidor e envia
            servidor = smtplib.SMTP(self.smtp_server, self.smtp_port)
            servidor.starttls() # Criptografia
            servidor.login(self.email_remetente, self.senha_app)
            servidor.send_message(mensagem)
            servidor.quit()
            print("✅ E-mail enviado com sucesso!")
            
        except Exception as e:
            print(f"⚠️ Erro ao enviar e-mail: {e}")