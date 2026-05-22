import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def send_verification_email(to: str, code: str) -> None:
    if ENVIRONMENT == "development": return

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Confirme seu email",
        "html": f"""
            <h2>Bem-vindo à Biblioteca Virtual!</h2>
            <p>Seu código de verificação é:</p>
            <h1 style="letter-spacing: 8px">{code}</h1>
            <p>Este código expira em 10 minutos.</p>
        """
    })

def send_email_change_email(to: str, code: str) -> None:
    if ENVIRONMENT == "development": return
    
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Confirme a troca de email",
        "html": f"""
            <h2>Confirmação de troca de email</h2>
            <p>Seu código de verificação é:</p>
            <h1 style="letter-spacing: 8px">{code}</h1>
            <p>Este código expira em 10 minutos.</p>
            <p>Se você não solicitou isso, ignore este email.</p>
        """
    })

def send_password_change_email(to: str, code: str) -> None:
    if ENVIRONMENT == "development": return

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Confirme a troca de senha",
        "html": f"""
            <h2>Confirmação de troca de senha</h2>
            <p>Seu código de verificação é:</p>
            <h1 style="letter-spacing: 8px">{code}</h1>
            <p>Este código expira em 10 minutos.</p>
            <p>Se você não solicitou isso, ignore este email.</p>
        """
    })

def send_password_changed_alert_email(to: str) -> None:
    if ENVIRONMENT == "development": return

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Senha alterada",
        "html": f"""
            <h2>A senha da sua conta foi alterada</h2>
            <p>Atenção! Se não foi você quem alterou a senha, <a href="">clique aqui para recuperá-la.</a></p>
        """
    })

def send_delete_confirmation(to: str, code: str) -> None:
    if ENVIRONMENT == "development": return
    
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": "Confirme a exclusão do seu usuário",
        "html": f"""
            <h2>Confirmação de exclusão de usuário</h2>
            <p>Seu código de verificação é:</p>
            <h1 style="letter-spacing: 8px">{code}</h1>
            <p>Este código expira em 10 minutos.</p>
            <p>Se você não solicitou isso, ignore este email.</p>
        """
    })