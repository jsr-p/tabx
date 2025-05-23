from tabx import Cell, Row, Table

F = Cell
tab = Table(rows=[Row([Cell("1")])])
tab_repr = repr(tab)
tab_render = tab.render()

tab2 = Table.from_cells(
    [
        [F("1"), F("2"), F("3"), F("4"), F("5")],
        [F("1"), F("2"), F("3"), F("4"), F("5")],
        [F("1"), F("2"), F("3"), F("4"), F("5")],
        [F("1"), F("2"), F("3"), F("4"), F("5")],
    ]
)
tab2_repr = repr(tab2)
tab2_render = tab2.render()
