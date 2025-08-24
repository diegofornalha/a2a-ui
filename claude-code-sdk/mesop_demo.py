import mesop as me
import mesop.labs as mel


@me.page(path="/", title="Mesop Demo - Neo4j Visualizer")
def main_page():
    me.text("🎯 Mesop UI Demo", type="headline-4")
    me.text("Bem-vindo ao Mesop - Framework Python para UI")
    
    with me.box(style=me.Style(
        padding=me.Padding.all(20),
        background="#f0f0f0",
        border_radius=10,
        margin=me.Margin.all(10)
    )):
        me.text("📊 Funcionalidades disponíveis:", style=me.Style(font_weight="bold"))
        me.text("• Interface reativa em Python puro")
        me.text("• Hot reload automático")
        me.text("• Componentes prontos para uso")
        me.text("• Sem necessidade de JavaScript/CSS")
    
    me.button("Clique aqui", on_click=on_click)
    
    if me.state(State).clicked:
        with me.box(style=me.Style(
            padding=me.Padding.all(15),
            background="#e3f2fd",
            border_radius=5,
            margin=me.Margin.symmetric(vertical=10)
        )):
            me.text(f"🎉 Botão clicado {me.state(State).click_count} vezes!")


@me.page(path="/text_to_text", title="Exemplo Text to Text")
def text_to_text_page():
    mel.text_to_text(
        process_text,
        title="Processador de Texto",
    )


def process_text(text: str):
    """Processa o texto e retorna em maiúsculas"""
    return f"Echo: {text.upper()}"


@me.stateclass
class State:
    clicked: bool = False
    click_count: int = 0


def on_click(e: me.ClickEvent):
    state = me.state(State)
    state.clicked = True
    state.click_count += 1


if __name__ == "__main__":
    me.run()