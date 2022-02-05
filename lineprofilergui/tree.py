import linecache
import pickle
import inspect
import hashlib
import os
import functools
import math

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt

from .utils import translate as _, MONOSPACE_FONT


def load_profile_data(filename):
    """Load line profiler data saved by kernprof module"""
    # stats has the following layout :
    # stats.timings =
    #     {(filename1, line_no1, function_name1):
    #         [(line_no1, hits1, total_time1),
    #          (line_no2, hits2, total_time2)],
    #      (filename2, line_no2, function_name2):
    #         [(line_no1, hits1, total_time1),
    #          (line_no2, hits2, total_time2),
    #          (line_no3, hits3, total_time3)]}
    # stats.unit = time_factor
    with open(filename, "rb") as fid:
        stats = pickle.load(fid)

    data = []
    for func_info, func_stats in stats.timings.items():
        # func_info is a tuple containing (filename, line, function name)
        func_data = FunctionData(func_info, func_stats, stats.unit)
        data.append(func_data)
    return data


class FunctionData:
    def __init__(self, func_info, stats, time_unit):
        self.filename, self.start_line_no, self.name = func_info
        self.filename = os.path.normpath(self.filename)
        self.total_time = 0.0
        self.was_called = False
        self.time_unit = time_unit

        self.load_code()
        self.parse_stats(stats)

    def load_code(self):
        # Note : linecache cache was checked at start of profiling
        # This way if the file has changed since the code ran there
        # is a chance that the correct version was in cache and we get
        # the correct lines.
        all_lines = linecache.getlines(self.filename)
        self.code_lines = inspect.getblock(all_lines[self.start_line_no :])

    def parse_stats(self, stats):
        self.line_data = []
        self.total_time = 0.0
        self.was_called = False
        next_stat_index = 0
        for line_no, code_line in enumerate(self.code_lines):
            line_no += self.start_line_no + 1  # Lines start at 1
            code_line = code_line.rstrip("\n")

            # stats contains data for runned lines only : (line_no, hits, total_time)
            if next_stat_index >= len(stats) or line_no != stats[next_stat_index][0]:
                # Line didn't run
                hits, line_total_time = None, None
            else:
                # Compute line times
                hits, line_total_time = stats[next_stat_index][1:]
                line_total_time *= self.time_unit
                self.total_time += line_total_time
                next_stat_index += 1
                self.was_called = True
            self.line_data.append(
                LineData(self, line_no, code_line, line_total_time, hits)
            )

    @functools.cached_property
    def color(self):
        """Choose deteministic unique color for the function"""
        md5 = hashlib.md5((self.filename + self.name).encode("utf8")).hexdigest()
        hue = (int(md5[:2], 16) - 68) % 360  # avoid blue (unreadable)
        color = QtGui.QColor.fromHsv(hue, 200, 255)
        return color

    def __iter__(self):
        yield from self.line_data


class LineData:
    def __init__(self, func_data, line_no, code, total_time, hits):
        self._func_data = func_data
        self.line_no = line_no
        self.code = code
        self.total_time = total_time
        self.hits = hits
        self.filename = func_data.filename

        self.func_total_time = None

    @property
    def percent_str(self):
        if self.total_time is None:
            return ""
        percent = 100 * self.total_time / self._func_data.total_time
        return f"{percent:.1f}"

    @property
    def time_str(self):
        if self.total_time is None:
            return ""
        return f"{self.total_time * 1e3:.3f}"

    @property
    def per_hit_str(self):
        if self.total_time is None:
            return ""
        return f"{self.total_time / self.hits * 1e3:.3f}"

    @property
    def hits_str(self):
        if self.hits is None:
            return ""
        return str(self.hits)

    @property
    def color(self):
        color = QtGui.QColor(self._func_data.color)  # Makes a copy
        ratio = self.total_time / self._func_data.total_time
        ratio = math.log10(9 * ratio + 1)  # Logarithmic while keeping 0 <= ratio <= 1
        color.setAlphaF(ratio)
        return QtGui.QBrush(color)


class ResultsTreeWidget(QtWidgets.QTreeWidget):
    """Tree widget to view line_profiler results"""

    goto_line = QtCore.Signal(str, int)  # Filename, line_no

    column_header_text = [
        _("Line #"),
        _("Hits"),
        _("Time (ms)"),
        _("Per Hit (ms)"),
        _("% Time"),
        _("Line Contents"),
    ]
    COL_0 = 0
    COL_NO = 0
    COL_HITS = 1
    COL_TIME = 2
    COL_PERHIT = 3
    COL_PERCENT = 4
    COL_LINE = 5
    COL_FILE_LINE = 0  # Not displayed but used to store data as Qt.UserRole

    CODE_NOT_RUN_COLOR = QtGui.QBrush(QtGui.QColor.fromRgb(128, 128, 128, 200))

    def __init__(self, parent):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setup_ui()

        self.profiledata = None

    def setup_ui(self):
        self.setColumnCount(len(self.column_header_text))
        self.setHeaderLabels(self.column_header_text)
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.setProperty("showDropIndicator", False)
        self.setUniformRowHeights(True)
        self.setSortingEnabled(False)
        self.setItemsExpandable(True)
        self.setDragEnabled(False)

        self.itemActivated.connect(self.item_activated)

    def load_data(self, filename):
        self.profiledata = load_profile_data(filename)
        self.show_tree()

    def show_tree(self):
        """Populate the tree with line profiler data and display it."""
        self.clear()  # Clear before re-populating
        self.populate_tree()

        self.expandAll()
        for col in range(self.columnCount() - 1):
            self.resizeColumnToContents(col)

        if self.topLevelItemCount() > 1:
            self.collapseAll()

    def populate_tree(self):
        """Create each item (and associated data) in the tree"""
        if not self.profiledata:
            self.warn_no_data()
            return

        for func_data in self.profiledata:
            # Function name and position
            func_item = QtWidgets.QTreeWidgetItem(self)
            func_item.setData(
                self.COL_0,
                Qt.DisplayRole,
                _(
                    '{func_name} ({time_ms:.3f}ms) in file "{filename}", line {line_no}'
                ).format(
                    filename=func_data.filename,
                    line_no=func_data.start_line_no,
                    func_name=func_data.name,
                    time_ms=func_data.total_time * 1e3,
                ),
            )
            func_item.setFirstColumnSpanned(True)
            if not func_data.was_called:
                func_item.setForeground(self.COL_0, self.CODE_NOT_RUN_COLOR)

            # Lines of code
            for line_data in func_data:
                line_item = QtWidgets.QTreeWidgetItem(func_item)
                self.fill_line_item(line_item, line_data)

                # Color background
                if line_data.total_time is not None:
                    color = line_data.color
                    for col in range(self.columnCount()):
                        line_item.setBackground(col, color)
                else:
                    for col in range(self.columnCount()):
                        line_item.setForeground(col, self.CODE_NOT_RUN_COLOR)

    def fill_line_item(self, item, line_data):
        item.setData(
            self.COL_FILE_LINE, Qt.UserRole, (line_data.filename, line_data.line_no),
        )
        item.setData(self.COL_NO, Qt.DisplayRole, line_data.line_no)
        item.setData(
            self.COL_PERCENT, Qt.DisplayRole, line_data.percent_str,
        )
        item.setTextAlignment(self.COL_PERCENT, Qt.AlignCenter)
        item.setData(self.COL_TIME, Qt.DisplayRole, line_data.time_str)
        item.setTextAlignment(self.COL_TIME, Qt.AlignCenter)
        item.setData(self.COL_PERHIT, Qt.DisplayRole, line_data.per_hit_str)
        item.setTextAlignment(self.COL_PERHIT, Qt.AlignCenter)
        item.setData(self.COL_HITS, Qt.DisplayRole, line_data.hits_str)
        item.setTextAlignment(self.COL_HITS, Qt.AlignCenter)
        item.setData(self.COL_LINE, Qt.DisplayRole, line_data.code)
        item.setFont(self.COL_LINE, MONOSPACE_FONT)

    def warn_no_data(self):
        warn_item = QtWidgets.QTreeWidgetItem(self)
        warn_item.setData(
            self.COL_0,
            Qt.DisplayRole,
            _("No timings to display. Did you forget to add @profile decorators ?"),
        )
        warn_item.setFirstColumnSpanned(True)
        warn_item.setTextAlignment(self.COL_0, Qt.AlignCenter)
        font = warn_item.font(self.COL_0)
        font.setStyle(QtGui.QFont.StyleItalic)
        warn_item.setFont(self.COL_0, font)

    def item_activated(self, item):
        if not item.isFirstColumnSpanned():  # Skip parent lines
            filename, line_no = item.data(self.COL_FILE_LINE, Qt.UserRole)
            self.goto_line.emit(filename, line_no)