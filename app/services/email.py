import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def setRecipient(to: str) -> str:
    return to if "ENVIRONMENT" == "production" else "pauloricardo.torre@gmail.com"


def send_verification_email(to: str, code: str) -> None:
    recipient = setRecipient(to)

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
        "subject": "Confirme seu email",
        "html": f"""
            <h2>Bem-vindo à Biblioteca Virtual!</h2>
            <p>Seu código de verificação é:</p>
            <h1 style="letter-spacing: 8px">{code}</h1>
            <p>Este código expira em 10 minutos.</p>
        """
    })

def send_email_change_email(to: str, code: str) -> None:
    recipient = setRecipient(to)
    
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
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
    recipient = setRecipient(to)

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
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
    recipient = setRecipient(to)

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
        "subject": "Senha alterada",
        "html": f"""
            <h2>A senha da sua conta foi alterada</h2>
            <p>Atenção! Se não foi você quem alterou a senha, <a href="">clique aqui para recuperá-la.</a></p>
        """
    })

def send_delete_confirmation(to: str, code: str) -> None:
    recipient = setRecipient(to)
    
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
        "subject": "Confirme a exclusão do seu usuário",
        "html": f"""
            <h2>Confirmação de exclusão de usuário</h2>
            <p>Seu código de verificação é:</p>
            <h1 style="letter-spacing: 8px">{code}</h1>
            <p>Este código expira em 10 minutos.</p>
            <p>Se você não solicitou isso, ignore este email.</p>
        """
    })