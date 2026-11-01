from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static


class PlaceholderScreen(Container):
    def __init__(self, title: str, description: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description

    def compose(self) -> ComposeResult:
        yield Static(self.title, classes="section-title")
        yield Static(self.description, classes="muted")
        yield Static("This screen is ready for its backend adapter.", classes="empty-state")
