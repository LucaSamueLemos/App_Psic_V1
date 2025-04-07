import flet as ft
import calendar
from datetime import datetime
from database import Database

db = Database()

class Calendar:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_date = datetime.now()
        self.selected_date = None  # Novo atributo para rastrear a seleção
        self.grid = ft.GridView(
            expand=True,
            runs_count=7,
            max_extent=50,
            spacing=2,
            run_spacing=2,
            padding=10
        )
        self.entries = []
        self.load_entries()

    def load_entries(self):
        user_id = self.page.session.get("user_id")
        self.entries = db.get_month_entries(
            user_id=user_id,
            year=self.current_date.year,
            month=self.current_date.month
        )

    def create_header(self):
        return ft.Column([
            ft.Text(
                f"{self.current_date.strftime('%B').upper()} {self.current_date.year}",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Row([
                ft.IconButton(
                    ft.icons.CHEVRON_LEFT,
                    on_click=lambda _: self.change_month(-1)
                ),
                ft.IconButton(
                    ft.icons.CHEVRON_RIGHT,
                    on_click=lambda _: self.change_month(1)
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

    def change_month(self, delta):
        month = self.current_date.month + delta
        year = self.current_date.year
        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1

        self.current_date = datetime(year, month, 1)
        self.selected_date = None  # Reseta a seleção ao mudar de mês
        self.load_entries()
        self.update_calendar()

    def get_day_entries(self, day):
        target_date = f"{self.current_date.year}-{self.current_date.month:02}-{day:02}"
        return [entry for entry in self.entries if entry[0].startswith(target_date)]

    def create_day_content(self, day, is_current_month):
        entries = self.get_day_entries(day)
        content = []
        if is_current_month:
            content.append(ft.Text(str(day), size=16, weight=ft.FontWeight.BOLD))
            if entries:
                emotion = entries[0][1].split()[0]
                content.append(ft.Text(emotion, size=20))
        return ft.Column(
            content,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def create_day(self, day, is_current_month):
        entries = self.get_day_entries(day)
        
        # Verifica se o dia está selecionado
        is_selected = self.selected_date and \
                      self.selected_date.month == self.current_date.month and \
                      self.selected_date.day == day

        return ft.Container(
            content=self.create_day_content(day, is_current_month),
            width=50,
            height=50,
            border=ft.border.all(1, ft.colors.OUTLINE),
            bgcolor=ft.colors.BLUE_100 if is_selected else (ft.colors.SURFACE_VARIANT if entries else None),
            on_click=lambda e, d=day: self.select_day(d) if is_current_month else None,
            tooltip=f"Clique para detalhes" if is_current_month else None
        )

    def select_day(self, day):
        self.selected_date = datetime(
            self.current_date.year,
            self.current_date.month,
            day
        )
        self.show_day_details(day)
        self.update_calendar()

    def update_calendar(self):
        self.grid.controls.clear()

        cal = calendar.Calendar()
        month_days = cal.monthdays2calendar(
            self.current_date.year, 
            self.current_date.month
        )

        week_days = ["Do", "Se", "Te", "Qu", "Qu", "Se", "Sá"]
        for day in week_days:
            self.grid.controls.append(
                ft.Container(
                    content=ft.Text(day, weight=ft.FontWeight.BOLD, size=14),
                    alignment=ft.alignment.center,
                    width=50,
                    height=30,
                    bgcolor=ft.colors.TEAL_700,
                    border_radius=5
                )
            )

        for week in month_days:
            for day, weekday in week:
                if day == 0:
                    self.grid.controls.append(
                        ft.Container(
                            width=50,
                            height=50,
                            border=ft.border.all(0.5, ft.colors.OUTLINE),
                            bgcolor=ft.colors.BACKGROUND
                        )
                    )
                else:
                    self.grid.controls.append(
                        self.create_day(day, True)
                    )
        self.page.update()

    def show_day_details(self, day):
        entries = self.get_day_entries(day)
        if not entries:
            return

        content = []
        for entry in entries:
            date = datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S")
            content.extend([
                ft.Text(f"Data: {date.strftime('%d/%m/%Y %H:%M')}"),
                ft.Text(f"Emoção: {entry[1]}"),
                ft.Text(f"Notas: {entry[2] or 'Sem notas'}"),
                ft.Divider()
            ])

        dialog = ft.AlertDialog(
            title=ft.Text(f"Detalhes do dia {day}"),
            content=ft.Column(content, scroll=ft.ScrollMode.ALWAYS),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: self.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

def calendar_view(page: ft.Page):
    calendar = Calendar(page)
    calendar.update_calendar()
    
    return ft.View(
        "/calendar",
        controls=[
            ft.AppBar(
                title=ft.Text("Calendário"),
                actions=[
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: page.go("/main")
                    )
                ]
            ),
            ft.Container(
                content=calendar.create_header(),
                alignment=ft.alignment.center,
                padding=10
            ),
            ft.Container(
                content=calendar.grid,
                margin=ft.margin.all(10),
            ),
            ft.FloatingActionButton(
                icon=ft.icons.ARROW_BACK,
                text="Voltar",
                on_click=lambda _: page.go("/main")
            )
        ]
    )