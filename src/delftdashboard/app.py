"""Global application object for DelftDashboard."""

import os


class InfoPanel:
    """Wrapper around the documentation webpage widget."""

    def __init__(self):
        self.widget = None
        self.urls = {}

    def set_url(self, url):
        """Set the URL of the documentation panel directly."""
        if self.widget is not None:
            self.widget.set_url(url)

    def update(self, name):
        """Update the documentation panel to show the page for *name*."""
        url = self.urls.get(name, "")
        if url:
            self.set_url(url)


class DelftDashboard:
    def __init__(self):
        self.info = InfoPanel()

    def initialize(self):
        from .operations import initialize

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        initialize.initialize()


app = DelftDashboard()
