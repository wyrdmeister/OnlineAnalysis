# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Control - Plot dialog

Version 1.0

Michele Devetta (c) 2013


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import inspect
import math
import numpy as np

# PyQt
from PyQt4 import QtCore
from PyQt4 import QtGui

# Matplotlib stuff
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
#import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FormatStrFormatter

# GuiBase
from GuiBase import GuiBase
from GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAControl")

# Ui
from Ui import Ui_OAMultiplot


class PlotDialog(QtGui.QMainWindow, Ui_OAMultiplot, GuiBase):

    """ Create a plot dialog. """

    # Refresh signal
    refresh_signal = QtCore.pyqtSignal(list)

    def __init__(self, names, data, parent=None):
        """ Constructor. """
        # Parent constructor
        QtGui.QMainWindow.__init__(self, parent)
        GuiBase.__init__(self, "OAControl")
        self._parent = parent

        # Connect refresh signal
        self.refresh_signal.connect(self.on_draw)

        # Build UI
        self.setupUi(self)

        # Store names
        self.names = names

        # Figure
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)

        # Bind the 'pick' event for clicking on one of the bars
        self.canvas.mpl_connect('pick_event', self.on_pick)

        # Toolbar
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)

        # Layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        self.plot_area.setLayout(vbox)

        # Create colormap
        cdict = {'red': ((0.0, 1.0, 1.0),
                         (1e-6, 1.0, 0.5),
                         (0.3, 0.0, 0.0),
                         (0.7, 0.99, 0.99),
                         (1.0, 0.99, 0.99)),
                 'green': ((0.0, 1.0, 1.0),
                           (1e-6, 1.0, 0.99),
                           (0.3, 0.0, 0.0),
                           (0.7, 0.0, 0.0),
                           (1.0, 0.99, 0.99)),
                 'blue': ((0.0, 1.0, 1.0),
                          (1e-6, 1.0, 0.99),
                          (0.3, 0.99, 0.99),
                          (0.7, 0.0, 0.0),
                          (1.0, 0.0, 0.0))}

        self.cmap = LinearSegmentedColormap('root_cmap', cdict, 256)

        # Check that there are no scalars
        n = len(data)
        for i in range(n - 1, -1, -1):
            if not hasattr(data[i], 'shape'):
                del data[i]

        # Create subplots
        szx = int(math.ceil(math.sqrt(n)))
        szy = int(math.ceil(n / float(szx)))
        self.axes = []
        self.options = []
        for i in range(n):
            a = self.fig.add_subplot(szy, szx, i + 1)
            a.set_title(self.names[i])
            self.axes.append(a)
            self.options.append(dict(ptype=None, xautoscale=False, yautoscale=False, zautoscale=False))
            self.plot_selector.addItem(self.names[i])

        # Launch first refresh signal
        self.refresh_signal.emit(data)

    def resizeEvent(self, event):
        """ Handle the resize event of the window. """
        if event.size().isValid() and event.oldSize().isValid():
            w = event.size().width()
            h = event.size().height()
            dw = w - event.oldSize().width()
            dh = h - event.oldSize().height()
            self.logger.debug("[%s] Resized window to (%d, %d)", inspect.stack()[0][3], w, h)

            sz = self.plot_area.size()
            self.plot_area.resize(sz.width() + dw, sz.height() + dh)

            ps = self.close_button.pos()
            self.close_button.move(QtCore.QPoint(ps.x() + dw, ps.y() + dh))

            ps = self.control_frame.pos()
            self.control_frame.move(QtCore.QPoint(ps.x() + dw, ps.y()))

            # Change margins of plot_area
            sz = self.plot_area.size()
            w = float(sz.width())
            h = float(sz.height())
#            mg = [80., 40., 30., 60.]
#            self.fig.subplots_adjust(left=mg[0] / w,
#                                     right=(w - mg[1]) / w,
#                                     top=(h - mg[2]) / h,
#                                     bottom=mg[3] / h)

        else:
            QtGui.QMainWindow.resizeEvent(self, event)

    @QtCore.pyqtSlot(list)
    def on_draw(self, data):
        """ Redraws the figure. """
        # clear the axes and redraw the plot anew
        n = len(self.axes)
        if n > len(data):
            n = len(data)

        for i in range(n):

            # Split x and y
            if type(data[i]) is tuple:
                x = data[i][0]
                y = data[i][1]
            else:
                x = None
                y = data[i]

            # Discard scalars
            if type(y) is not np.ndarray:
                continue

            if self.options[i]['ptype'] is None:
                if len(y.shape) > 1:
                    # Plot a Pcolor
                    self.options[i]['ptype'] = "image"

                else:
                    # Plot a line
                    if x is None:
                        self.options[i]['ptype'] = "yplot"
                    else:
                        self.options[i]['ptype'] = "xyplot"
                # Reselect current plot
                self.plot_selector.setCurrentIndex(self.plot_selector.currentIndex())

            if self.options[i]['ptype'] == "image":
                if len(self.axes[i].images) == 0:
                    # No image plotted yet
                    im = self.axes[i].imshow(y, cmap=self.cmap, aspect="equal")
                    # Create colorbar if needed
                    if not hasattr(self.axes[i], 'cb'):
                        self.axes[i].cb = self.fig.colorbar(im, ax=self.axes[i])
                        # Set smaller font on ticks
                        for t in self.axes[i].cb.ax.get_yticklabels():
                            t.set_fontsize(9)
                    # Set zscale
                    self.options[i]['zscale'] = [0, np.max(y)]
                else:
                    self.axes[i].images[0].set_array(y)

                # Update CLIM
                if self.options[i]['zautoscale']:
                    self.axes[i].images[0].set_clim(0, np.max(y))
                else:
                    self.axes[i].images[0].set_clim(self.options[i]['zscale'])

                # Set exponential notation in colorbar ticks if max >= 1000
                if np.max(y) >= 1000:
                    self.axes[i].cb.formatter = FormatStrFormatter("%.1e")

            elif self.options[i]['ptype'] == "hist2d":
                if x is None:
                    pass
                else:
                    (h, x, y) = np.histogram2d(x, y, 100)
                    if len(self.axes[i].images) == 0:
                    #if len(self.axes[i].collections) == 0:
                        #pc = self.axes[i].pcolor(x, y, h, cmap=self.cmap)
                        pc = self.axes[i].imshow(np.rollaxis(h.T, 1), cmap=self.cmap, extent=[x[0], x[-1], y[0], y[-1]], aspect="auto")
                        # Create colorbar if needed
                        if not hasattr(self.axes[i], 'cb'):
                            self.axes[i].cb = self.fig.colorbar(pc, ax=self.axes[i])
                            # Set smaller font on ticks
                            for t in self.axes[i].cb.ax.get_yticklabels():
                                t.set_fontsize(9)
                    else:
                        pass
                        #self.axes[i].images[0].set_array(h)

            elif self.options[i]['ptype'] == "xyplot":
                if len(self.axes[i].lines) == 0:
                    self.axes[i].plot(x, y)
                else:
                    if x is None:
                        x = self.axes[i].lines[0].get_xdata()
                    self.axes[i].lines[0].set_data(x, y)
                # Set scale
                if self.options[i]['xautoscale']:
                    self.axes[i].set_xlim(np.min(x), np.max(x))
                if self.options[i]['yautoscale']:
                    self.axes[i].set_ylim(np.min(y), np.max(y))

            elif self.options[i]['ptype'] == "yplot":
                if len(self.axes[i].lines) == 0:
                    self.axes[i].plot(y)
                else:
                    self.axes[i].lines[0].set_data(np.arange(len(y)), y)
                # Set scale
                if self.options[i]['xautoscale']:
                    self.axes[i].set_xlim(0, y.shape[0])
                if self.options[i]['yautoscale']:
                    self.axes[i].set_ylim(np.min(y), np.max(y))
            else:
                pass

        # Redraw canvas
        self.canvas.draw()

        self.update_controls(self.plot_selector.currentIndex())

    @QtCore.pyqtSlot(QtCore.QEvent)
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        self.logger.debug("[%s] Called on_pick(). Event: %s", inspect.stack()[0][3], event)

    @QtCore.pyqtSlot()
    def on_close_button_released(self):
        """ Slot for close button. """
        self.close()

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """ Handler for close event. """
        self._parent.dialogs.remove(self)
        return QtGui.QMainWindow.closeEvent(self, event)

    @QtCore.pyqtSlot()
    def on_plot_scatter_released(self):
        """ Convert a line plot to a scatter plot. """
        # Get axes
        i = self.plot_selector.currentIndex()
        axes = self.axes[i]

        # Modify plot
        axes.get_lines()[0].set_marker('o')
        axes.get_lines()[0].set_linewidth(0)

        # Redraw canvas
        self.canvas.draw()

    @QtCore.pyqtSlot()
    def on_plot_hist2d_released(self):
        """ Convert a x,y plot to a 2D histogram image. """
        # Get axes
        i = self.plot_selector.currentIndex()
        axes = self.axes[i]

        # Check plot type
        if self.options[i]['ptype'] not in ("xyplot"):
            # TODO: add a warning
            return

        # Enable 2D histogram
        self.options[i]['ptype'] = "hist2d"
        axes.lines = []

    @QtCore.pyqtSlot()
    def on_plot_reset_released(self):
        """ Reset plot. """
        index = self.plot_selector.currentIndex()
        self.axes[index].images = []
        self.axes[index].lines = []
        self.axes[index].collections = []

    @QtCore.pyqtSlot(int)
    def on_en_xautoscale_stateChanged(self, state):
        """ Toggle autoscale. """
        if state == QtCore.Qt.Checked:
            self.options[self.plot_selector.currentIndex()]['xautoscale'] = True
        else:
            self.options[self.plot_selector.currentIndex()]['xautoscale'] = False

    @QtCore.pyqtSlot(int)
    def on_en_yautoscale_stateChanged(self, state):
        """ Toggle autoscale. """
        if state == QtCore.Qt.Checked:
            self.options[self.plot_selector.currentIndex()]['yautoscale'] = True
        else:
            self.options[self.plot_selector.currentIndex()]['yautoscale'] = False

    @QtCore.pyqtSlot(int)
    def on_en_zautoscale_stateChanged(self, state):
        """ Toggle autoscale. """
        if state == QtCore.Qt.Checked:
            self.options[self.plot_selector.currentIndex()]['zautoscale'] = True
            self.zmin_slider.setSliderPosition(0)
            self.zmax_slider.setSliderPosition(99)
        else:
            self.options[self.plot_selector.currentIndex()]['zautoscale'] = False

    @QtCore.pyqtSlot(int)
    def on_zmin_slider_valueChanged(self, value):
        # Index
        index = self.plot_selector.currentIndex()

        # Get image maximum
        zmax = np.max(self.axes[index].images[0].get_array())

        # Value
        val = zmax * (value + 1) / 100

        # Update label
        self.zmin_value.setText("%.2f" % (val, ))

        # Update plot clim
        self.options[index]['zscale'][0] = val

    @QtCore.pyqtSlot(int)
    def on_zmax_slider_valueChanged(self, value):
        # Index
        index = self.plot_selector.currentIndex()

        # Get image maximum
        zmax = np.max(self.axes[index].images[0].get_array())

        # Value
        val = zmax * (value + 1) / 100

        # Update label
        self.zmax_value.setText("%.2f" % (val, ))

        # Update plot clim
        self.options[index]['zscale'][1] = val

    @QtCore.pyqtSlot(int)
    def on_plot_selector_currentIndexChanged(self, index):
        """ Called when the currently selected plot has changed. """
        self.logger.debug("[%s] Changed selection to plot %d with title '%s'.", inspect.stack()[0][3], index, self.names[index])

        # Set autoscale status
        if self.options[index]['xautoscale']:
            self.en_xautoscale.setCheckState(QtCore.Qt.Checked)
        else:
            self.en_xautoscale.setCheckState(QtCore.Qt.Unchecked)
        if self.options[index]['yautoscale']:
            self.en_yautoscale.setCheckState(QtCore.Qt.Checked)
        else:
            self.en_yautoscale.setCheckState(QtCore.Qt.Unchecked)
        if self.options[index]['zautoscale']:
            self.en_zautoscale.setCheckState(QtCore.Qt.Checked)
        else:
            self.en_zautoscale.setCheckState(QtCore.Qt.Unchecked)

        self.update_controls(index)

    def update_controls(self, index):
        # Enable / disable relevand buttons
        if self.options[index]['ptype'] in ("image", "hist2d"):
            self.plot_scatter.setDisabled(True)
            self.plot_hist2d.setDisabled(True)
            self.en_xautoscale.setDisabled(False)
            self.en_yautoscale.setDisabled(False)
            self.en_zautoscale.setDisabled(False)
            self.zmin_slider.setDisabled(False)
            self.zmax_slider.setDisabled(False)

            if self.options[index]['ptype'] == "hist2d":
                self.hist_xbin.setDisabled(False)
                self.hist_ybin.setDisabled(False)
            else:
                self.hist_xbin.setDisabled(True)
                self.hist_ybin.setDisabled(True)

        elif self.options[index]['ptype'] in ("xyplot", ):
            self.plot_scatter.setDisabled(False)
            self.plot_hist2d.setDisabled(False)
            self.en_xautoscale.setDisabled(False)
            self.en_yautoscale.setDisabled(False)
            self.en_zautoscale.setDisabled(True)
            self.zmin_slider.setDisabled(True)
            self.zmax_slider.setDisabled(True)
            self.hist_xbin.setDisabled(False)
            self.hist_ybin.setDisabled(False)

        elif self.options[index]['ptype'] in ("yplot", ):
            self.plot_scatter.setDisabled(True)
            self.plot_hist2d.setDisabled(True)
            self.en_xautoscale.setDisabled(False)
            self.en_yautoscale.setDisabled(False)
            self.en_zautoscale.setDisabled(True)
            self.zmin_slider.setDisabled(True)
            self.zmax_slider.setDisabled(True)
            self.hist_xbin.setDisabled(True)
            self.hist_ybin.setDisabled(True)

        else:
            self.plot_scatter.setDisabled(True)
            self.plot_hist2d.setDisabled(True)
            self.en_xautoscale.setDisabled(True)
            self.en_yautoscale.setDisabled(True)
            self.en_zautoscale.setDisabled(True)
            self.zmin_slider.setDisabled(True)
            self.zmax_slider.setDisabled(True)
            self.hist_xbin.setDisabled(True)
            self.hist_ybin.setDisabled(True)