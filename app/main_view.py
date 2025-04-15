import flet as ft
from datetime import datetime
from database import Database
import google.generativeai as genai

# ======= CONFIGURAÇÕES DA API GEMINI =======
API_KEY = "AIzaSyBwXURLnih2nZ16JmdoEB6awPrYgEZrEVk"
genai.configure(api_key=API_KEY)

# ======= INICIALIZA MODELO GEMINI =======
model = genai.GenerativeModel("gemini-2.0-flash")
historico = []

# ======= FUNÇÃO DE RESPOSTA COM IA USANDO CONTEXTO =======
def ia_responder(mensagem):
    try:
        historico.append({"role": "user", "parts": [mensagem]})
        resposta = model.generate_content(historico)
        historico.append({"role": "model", "parts": [resposta.text.strip()]})
        return resposta.text.strip()
    except Exception as e:
        return f"Erro ao chamar IA: {e}"

# ======= CRIAÇÃO DE BALÕES DE CHAT =======
def criar_balao(mensagem, tipo="user"):
    if tipo == "user":
        return ft.Container(
            content=ft.Text(mensagem, color=ft.colors.WHITE),
            bgcolor=ft.colors.BLUE_600,
            padding=10,
            border_radius=15,
            alignment=ft.alignment.center_right,
            margin=5
        )
    else:
        return ft.Container(
            content=ft.Text(mensagem, color=ft.colors.BLACK),
            bgcolor=ft.colors.GREY_300,
            padding=10,
            border_radius=15,
            alignment=ft.alignment.center_left,
            margin=5
        )

# ======= MAIN VIEW PRINCIPAL COM IA INTEGRADA =======
db = Database()

def main_view(page: ft.Page):
    emotions = ['😊 Feliz', '😢 Triste', '😡 Raiva', '😲 Surpreso', '😰 Ansioso', '😌 Calmo', '🤮 Enjoado']
    
    selected_emotion = ft.Dropdown(
        options=[ft.dropdown.Option(e) for e in emotions],
        label="Selecione seu humor",
        value=emotions[0],
        expand=True
    )

    chat = ft.ListView(expand=True, spacing=5, auto_scroll=True, padding=10)
    notes_field = ft.TextField(label="Notas adicionais", multiline=True, expand=True)
    user_message = ft.TextField(
    label="Digite sua mensagem",
    expand=True,
    on_submit=lambda e: enviar_mensagem(user_message.value)
)


    def enviar_mensagem(texto):
        if texto.strip() == "":
            return

        # Mensagem do usuário
        chat.controls.append(criar_balao(f"Você: {texto}", tipo="user"))
        page.update()

        # Loader temporário
        loader = criar_balao("IA está digitando...", tipo="ia")
        chat.controls.append(loader)
        page.update()

        # Obter resposta da IA
        resposta = ia_responder(texto)

        # Remover loader
        chat.controls.remove(loader)

        # Adicionar resposta da IA
        chat.controls.append(criar_balao(f"IA: {resposta}", tipo="ia"))
        user_message.value = ""
        page.update()


    def on_send_click(e):
        enviar_mensagem(user_message.value)

    def save_entry(e):
        user_id = page.session.get("user_id")
        if not user_id:
            show_snackbar("Erro: Usuário não identificado!", error=True)
            return
        
        if not selected_emotion.value:
            show_snackbar("Selecione uma emoção antes de salvar!", error=True)
            return
        
        chat_text = "\n".join([
            c.content.value for c in chat.controls if isinstance(c, ft.Container) and isinstance(c.content, ft.Text)
        ])

        db.save_mood_entry(
            user_id=user_id,
            emotion=selected_emotion.value,
            notes=notes_field.value,
            chat_history=chat_text
        )

        show_snackbar("Registro salvo com sucesso!", success=True)
        chat.controls.clear()
        notes_field.value = ""
        page.update()

    def show_snackbar(message, error=False, success=False):
        color = ft.colors.RED if error else ft.colors.GREEN if success else None
        page.snack_bar = ft.SnackBar(ft.Text(message, color=color))
        page.snack_bar.open = True
        page.update()

    return ft.View(
        "/main",
        controls=[
            ft.AppBar(
                title=ft.Text("Registro Diário"),
                actions=[
                    ft.IconButton(ft.icons.CALENDAR_MONTH, on_click=lambda _: page.go("/calendar")),
                    ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: page.go("/"))
                ]
            ),
            ft.Column([
                ft.Text("Selecione seu humor:", size=20),
                selected_emotion,
                ft.Divider(),

                # ====== Chat Gemini Aqui ======
                ft.Text("Chat com IA:", size=16),
                ft.Container(chat, height=200, bgcolor=ft.colors.SURFACE_VARIANT, padding=10, border_radius=10),
                ft.Row([user_message, ft.IconButton(ft.icons.SEND, on_click=on_send_click)]),

                ft.Divider(),
                ft.Text("Notas:", size=16),
                notes_field,
                ft.ElevatedButton("Salvar Registro", on_click=save_entry)
            ], spacing=10, expand=True)
        ]
    )
