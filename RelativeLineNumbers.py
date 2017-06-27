"""
File: RelativeLineNumbers.py
Author: Francesc Arpí @ 2017
"""

from sublime import Region
from sublime import Phantom
from sublime import PhantomSet
from sublime import LAYOUT_INLINE
from sublime_plugin import ViewEventListener

PACKAGE = "RelativeLineNumbers"
OPT_ENABLED = "relative_line_numbers_enabled"
OPT_ENABLED_DEFAULT = True
OPT_COLOR = "relative_line_numbers_color"
OPT_COLOR_DEFAULT = '#75715e'
OPT_COLOR_ZERO = "relative_line_numbers_zero_color"
OPT_COLOR_ZERO_DEFAULT = '#fd971f'


class RelativeLineNumbersEventListener(ViewEventListener):

    def __init__(self, view):
        self.view = view
        self.phantoms = PhantomSet(view, PACKAGE)
        self._render()

    def _tpl(self, color, line_number, text):
        return """
            <body id="{0}">
                <style>
                    .num{2} {{
                        padding-right: 4px;
                        color: {1};
                    }}
                </style>
                <div class="num{2}">{3}</div>
            </body>
        """.format(PACKAGE, color, line_number, text)

    def _value(self, line_number, current_line_num, last_line_num):
        value = 0
        if line_number < current_line_num:
            value = current_line_num - line_number
        elif line_number > current_line_num:
            value = line_number - current_line_num

        if value == 0:
            value = current_line_num + 1
            valuestr = current_line_num + 1

        valuestr = ('&nbsp;' * (len(str(last_line_num)) - len(str(value)))) + str(value)

        return value, valuestr

    def _render(self):

        settings = self.view.settings()

        if not settings.get(OPT_ENABLED, OPT_ENABLED_DEFAULT):
            return

        num_color = settings.get(OPT_COLOR, OPT_COLOR_DEFAULT)
        highlight_line_num_color = settings.get(OPT_COLOR_ZERO, OPT_COLOR_ZERO_DEFAULT)

        current_line_num = self.view.rowcol(self.view.sel()[0].begin())[0]
        last_line_num = self.view.rowcol(self.view.size())[0]
        visible_lines = self.view.lines(self.view.visible_region())
        visible_line_count = len(visible_lines)

        lines = self.view.lines(Region(
            self.view.text_point(current_line_num - visible_line_count, 0),
            self.view.text_point(current_line_num + visible_line_count, 0)))

        phantoms = []
        for line in lines:
            line_number = self.view.rowcol(line.a)[0]
            color = num_color if line_number != current_line_num else highlight_line_num_color

            phantoms.append(Phantom(
                line,
                self._tpl(color, *self._value(line_number, current_line_num, last_line_num)),
                LAYOUT_INLINE))

        self.phantoms.update(phantoms)

    def on_modified(self):
        self._render()

    def on_activated(self):
        self._render()

    def on_selection_modified(self):
        self._render()
