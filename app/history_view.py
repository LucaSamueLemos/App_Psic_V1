import flet as ft
from database import Database

db = Database()

def history_view(page: ft.Page):
    user_id = page.session.get("user_id")
    history_list = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO)

    def carregar_historico():
        history_list.controls.clear()
        registros = db.get_entries_by_user(user_id)

        if not registros:
            history_list.controls.append(ft.Text("Nenhum registro encontrado.", size=16))
            page.update()
            return

        # Agrupar por data
        datas = {}
        for entry in registros:
            data = entry["date"]
            if data not in datas:
                datas[data] = []
            datas[data].append(entry)

        for data, entradas in sorted(datas.items(), reverse=True):
            cards = []
            for e in entradas:
                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Emoção: {e['emotion']}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Notas: {e['notes'] or 'Sem observações.'}"),
                                ft.Text("Chat:", italic=True),
                                ft.Text(e["chat_history"] or "Sem conversa."),
                            ], spacing=5),
                            padding=10,
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            border_radius=10
                        )
                    )
                )
            history_list.controls.append(
                ft.Column([
                    ft.Text(f"📅 {data}", size=18, weight=ft.FontWeight.W_600),
                    *cards
                ], spacing=10)
            )
        page.update()

    page.on_view_pop = lambda _: page.go("/main")  # Voltar ao principal se sair da tela

    carregar_historico()

    return ft.View(
        "/calendar",
        controls=[
            ft.AppBar(title=ft.Text("Histórico por Data"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/main"))),
            ft.Container(history_list, padding=20, expand=True)
        ]
    )
