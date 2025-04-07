import flet as ft
from datetime import datetime
from database import Database

db = Database()

def main_view(page: ft.Page):
    emotions = ['😊 Feliz', '😢 Triste', '😡 Raiva', '😲 Surpreso', '😰 Ansioso', '😌 Calmo']
    
    selected_emotion = ft.Dropdown(
        options=[ft.dropdown.Option(e) for e in emotions],
        label="Selecione seu humor",
        value=emotions[0],  # Define um valor inicial
        expand=True
    )

    chat_history = ft.ListView(expand=True, auto_scroll=True)
    notes_field = ft.TextField(label="Notas adicionais", multiline=True, expand=True)
    user_message = ft.TextField(label="Digite sua mensagem", expand=True)

    def send_message(e):
        if user_message.value.strip():
            chat_history.controls.append(ft.Text(f"Você: {user_message.value}", weight=ft.FontWeight.BOLD))
            chat_history.controls.append(ft.Text("IA: Como posso ajudá-lo com isso?", italic=True))
            user_message.value = ""
            page.update()

    def save_entry(e):
        user_id = page.session.get("user_id")
        if not user_id:
            show_snackbar("Erro: Usuário não identificado!", error=True)
            return
        
        if not selected_emotion.value:
            show_snackbar("Selecione uma emoção antes de salvar!", error=True)
            return
        
        chat_text = "\n".join([c.value for c in chat_history.controls if isinstance(c, ft.Text)])

        db.save_mood_entry(
            user_id=user_id,
            emotion=selected_emotion.value,
            notes=notes_field.value,
            chat_history=chat_text
        )

        show_snackbar("Registro salvo com sucesso!", success=True)
        chat_history.controls.clear()
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
                ft.Text("Chat com IA:", size=16),
                ft.Container(chat_history, height=200, bgcolor=ft.colors.SURFACE_VARIANT, padding=10),
                ft.Row([user_message, ft.IconButton(ft.icons.SEND, on_click=send_message)]),
                ft.Divider(),
                ft.Text("Notas:", size=16),
                notes_field,
                ft.ElevatedButton("Salvar Registro", on_click=save_entry)
            ], spacing=10, expand=True)
        ]
    )
