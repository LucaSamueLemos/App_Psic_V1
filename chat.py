import flet as ft
import google.generativeai as genai

# ======= CONFIGURAÇÕES DA API GEMINI =======
API_KEY = "AIzaSyBwXURLnih2nZ16JmdoEB6awPrYgEZrEVk"  # 🔐 Coloque sua chave da API Gemini aqui
genai.configure(api_key=API_KEY)

# ======= INICIALIZA MODELO GEMINI =======
model = genai.GenerativeModel("gemini-2.0-flash")

# ======= HISTÓRICO GLOBAL =======
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

def criar_balao(mensagem, tipo="user"):
    if tipo == "user":
        return ft.Container(
            content=ft.Text(mensagem, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE_600,
            padding=10,
            border_radius=15,
            alignment=ft.alignment.center_right,
            margin=5
        )
    else:  # tipo == "ia"
        return ft.Container(
            content=ft.Text(mensagem, color=ft.Colors.BLACK),
            bgcolor=ft.Colors.GREY_300,
            padding=10,
            border_radius=15,
            alignment=ft.alignment.center_left,
            margin=5
        )

def main(page: ft.Page):
    page.title = "Chat com IA (Gemini)"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 30
    page.bgcolor = ft.Colors.GREY_100

    chat = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
        auto_scroll=True,  # Isso faz o scroll automático
    )

    campo_texto = ft.TextField(
        label="Digite sua mensagem",
        multiline=False,
        expand=True,
        on_submit=lambda e: enviar_mensagem(e.control.value)
    )

    def enviar_mensagem(texto):
        if texto.strip() == "":
            return

        chat.controls.append(criar_balao(f"Você: {texto}", tipo="user"))
        page.update()

        resposta = ia_responder(texto)
        chat.controls.append(criar_balao(f"IA: {resposta}", tipo="ia"))
        campo_texto.value = ""
        page.update()

    enviar_btn = ft.IconButton(
        icon=ft.Icons.SEND,
        on_click=lambda e: enviar_mensagem(campo_texto.value)
    )

    chat_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Assistente IA", size=20, weight=ft.FontWeight.W_600),
                    ft.Divider(),
                    ft.Container(
                        content=chat,
                        height=400,  # Altura definida para o scroll funcionar
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10
                    ),
                    ft.Row([campo_texto, enviar_btn], spacing=10),
                ],
                expand=True
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            expand=True,
        ),
        elevation=8,
    )

    page.add(chat_card)

ft.app(target=main)
