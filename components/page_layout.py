"""
Componente de layout reutilizável seguindo as melhores práticas do Mesop
"""

import mesop as me


@me.content_component
def page_container():
    """Container principal da página com estilo consistente"""
    with me.box(
        style=me.Style(
            max_width="1200px",
            margin=me.Margin.symmetric(horizontal="auto"),
            padding=me.Padding.all(24),
            background="#f8f9fa",
            min_height="100vh"
        )
    ):
        me.slot()


@me.content_component
def section_header(title: str, subtitle: str = ""):
    """Cabeçalho de seção reutilizável"""
    with me.box(
        style=me.Style(
            margin=me.Margin(bottom=24),
            padding=me.Padding(bottom=16),
            border_bottom=me.BorderSide(color="#e9ecef", width=1)
        )
    ):
        me.text(
            title,
            style=me.Style(
                font_size=28,
                font_weight="bold",
                color="#2c3e50",
                margin=me.Margin(bottom=4)
            )
        )
        if subtitle:
            me.text(
                subtitle,
                style=me.Style(
                    font_size=16,
                    color="#6c757d"
                )
            )


@me.content_component
def status_indicator(status: str, message: str):
    """Indicador de status reutilizável"""
    status_colors = {
        "success": "#28a745",
        "warning": "#ffc107", 
        "error": "#dc3545",
        "info": "#17a2b8"
    }
    
    color = status_colors.get(status, "#6c757d")
    
    with me.box(
        style=me.Style(
            display="flex",
            align_items="center",
            gap=8,
            padding=me.Padding.all(12),
            background=color,
            color="white",
            border_radius=6,
            margin=me.Margin(bottom=16)
        )
    ):
        me.text(message)


@me.content_component
def loading_spinner(message: str = "Carregando..."):
    """Spinner de carregamento reutilizável"""
    with me.box(
        style=me.Style(
            display="flex",
            align_items="center",
            justify_content="center",
            gap=12,
            padding=me.Padding.all(20)
        )
    ):
        me.progress_spinner()
        me.text(message) 