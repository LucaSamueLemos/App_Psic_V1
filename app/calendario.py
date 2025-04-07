import flet as ft
import calendar
from datetime import datetime

def main(page: ft.Page):
    page.title = "Calendário Interativo"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    
    # Variáveis de estado
    current_date = datetime.today()
    selected_date = None

    # Componentes da UI
    month_year = ft.Text(current_date.strftime("%B %Y"), size=20, weight="bold")
    grid_dias = ft.GridView(expand=1, runs_count=7, spacing=5)

    def construir_calendario():
        grid_dias.controls.clear()
        
        # Cabeçalho com dias da semana
        for dia in ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]:
            grid_dias.controls.append(
                ft.Container(
                    content=ft.Text(dia, weight="bold"),
                    alignment=ft.alignment.center,
                    border=ft.border.all(1, "#e0e0e0"),
                    padding=5,
                )
            )

        # Dias do mês
        cal = calendar.Calendar(firstweekday=6)  # Começa no domingo
        for dia in cal.monthdayscalendar(current_date.year, current_date.month):
            for d in dia:
                cor_fundo = ft.colors.BLUE if (selected_date and d == selected_date.day 
                                             and current_date.month == selected_date.month 
                                             and current_date.year == selected_date.year) else None
                
                grid_dias.controls.append(
                    ft.Container(
                        content=ft.Text(str(d) if d != 0 else ""),
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, "#e0e0e0"),
                        bgcolor=cor_fundo,
                        padding=5,
                        on_click=lambda e, d=d: selecionar_dia(d) if d != 0 else None,
                    )
                )

    def mudar_mes(e, direcao):
        nonlocal current_date
        mes = current_date.month + direcao
        ano = current_date.year
        
        if mes == 0:
            mes = 12
            ano -= 1
        elif mes == 13:
            mes = 1
            ano += 1
            
        current_date = current_date.replace(year=ano, month=mes, day=1)
        month_year.value = current_date.strftime("%B %Y")
        construir_calendario()
        page.update()

    def selecionar_dia(dia):
        nonlocal selected_date
        selected_date = datetime(current_date.year, current_date.month, dia)
        construir_calendario()
        page.update()
        print("Dia selecionado:", selected_date.strftime("%d/%m/%Y"))

    # Botões de navegação
    botoes = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda e: mudar_mes(e, -1)
            ),
            month_year,
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda e: mudar_mes(e, 1)
            ),
        ],
        alignment="center"
    )

    # Construir calendário inicial
    construir_calendario()

    # Adicionar componentes à página
    page.add(
        ft.Column(
            [
                botoes,
                ft.Container(
                    content=grid_dias,
                    width=500,
                    height=300,
                    padding=10,
                    border=ft.border.all(1, "#e0e0e0"),
                    border_radius=10,
                )
            ],
            spacing=20
        )
    )

ft.app(target=main)