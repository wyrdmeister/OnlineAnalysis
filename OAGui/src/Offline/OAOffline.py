# -*- coding: utf-8 -*-
"""
Online Analysis - Offline OA interface

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

import os
import inspect
import Queue
import multiprocessing

# Logger server
from OACommon import LoggerServer

# PyQt
from PyQt4 import QtCore
from PyQt4 import QtGui

# Editor base
from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAOffline")

# OA worker
from OAProcess import OfflineWorker

# Dialogs
from OADialogs import OASelect
from OADialogs import OAProgress

# Result model
from OAResultModel import ResultModel
from OAResultModel import PushButtonDelegate

# Ui
from Ui import Ui_OAOffline


class MainWindow(QtGui.QMainWindow, GuiBase, Ui_OAOffline):

    """ Main window class. """

    ### Logger signal
    log_signal = QtCore.pyqtSignal(unicode)

    def __init__(self, parent=None):
        """ Constructor. """
        # Parent constructors
        QtGui.QMainWindow.__init__(self, parent)
        GuiBase.__init__(self, "OAOffline")

        # Setup UI
        self.setupUi(self)

        # Setup widget logger
        self.logger.setupWidgetLogger(self.log_signal)
        self.log_signal.connect(self.update_log)

        # Create LoggerServer for the OA
        try:
            self.logserver = LoggerServer("OAOfflineSrv", self.logger.level())
            self.logserver.start()
        except Exception, e:
            self.logger.error("[%s] Cannot init LogServer (Error: %s)", inspect.stack()[0][3], e)
            self.logserver = None

        # Start timer
        self.timer = self.startTimer(500)

        # Plot dialog list
        self.dialogs = []

    ##
    ## Button slots
    ##
    @QtCore.pyqtSlot()
    def on_config_browse_released(self):
        """ Open file browser to select the configuration file. """
        # Call file dialog
        name = unicode(QtGui.QFileDialog.getOpenFileName(
                            self,
                            _trUtf8("Open configuration file"),
                            os.getcwd(),
                            _trUtf8("Configuration file (*.xml)")))
        if name != "":
            # Relative paths works reliably only on posix systems. On windows
            # we just use absolute paths
            if os.name == 'posix':
                # Get path relative to cwd
                relname = os.path.relpath(name, os.getcwd())
                # Count number of relative levels
                count = 0
                for el in relname.split(os.path.sep):
                    if el == os.path.pardir:
                        count += 1
                    else:
                        break
                # If number of levels is less than 3, use relative path
                if count < 3:
                    name = relname
            self.logger.debug("[%s] Selected file '%s'.", inspect.stack()[0][3], name)
            self.config_file.setText(name)

    @QtCore.pyqtSlot()
    def on_inpath_browse_released(self):
        """ Open a directory browser to get the source directory. """
        name = unicode(QtGui.QFileDialog.getExistingDirectory(
                                self,
                                _trUtf8("Select source directory"),
                                self.inpath.currentText(),
                                    QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.DontUseNativeDialog))
        if name != "" and name != unicode(self.inpath.currentText()):
            for i in range(self.inpath.count()):
                if name == unicode(self.inpath.itemText(i)):
                    break
            else:
                self.inpath.addItem(name)
            self.logger.debug("[%s] Added source directory '%s'", inspect.stack()[0][3], name)
            # Select the new name
            for i in range(self.inpath.count()):
                if name == unicode(self.inpath.itemText(i)):
                    self.inpath.setCurrentIndex(i)
                    break

    @QtCore.pyqtSlot()
    def on_start_button_released(self):
        """ Start button slot. """
        if unicode(self.inpath.currentText()) != "" and unicode(self.config_file.text()) != "":

            # Start dialog to select files to process
            dg = OASelect(unicode(self.inpath.currentText()), self)
            ans = dg.exec_()
            if ans == QtGui.QDialog.Accepted:
                self.logger.debug("[%s] Selected %d files to process.", inspect.stack()[0][3], len(dg.files))
            else:
                self.logger.debug("[%s] Selection cancelled.", inspect.stack()[0][3])
                return
            # Get list of files
            files = dg.files
            files.reverse()

            # Create processing worker
            job_queue = multiprocessing.Queue()
            res_queue = multiprocessing.Queue()
            worker = OfflineWorker(unicode(self.config_file.text()), job_queue, res_queue, self.logger.level(), None)
            worker.start()

            # Open progress dialog
            dg = OAProgress(len(files), self)
            dg.setModal(True)
            dg.show()

            # Cycle over files
            job_list = []
            out_files = []
            while True:
                if job_queue.qsize() < 2 and len(files) > 0:
                    name = files.pop()
                    self.logger.debug("[%s] Submitting file '%s'", inspect.stack()[0][3], name)
                    job_queue.put(name)
                    job_list.append(name)

                # Call process event to keep the dialog responsive
                QtGui.QApplication.processEvents()

                try:
                    # Get a file to process from the queue. If the file is None
                    # terminate.
                    res = res_queue.get(timeout=0.05)
                    self.logger.debug("[%s] Terminated processing of file '%s'.", inspect.stack()[0][3], res[1])

                    # Check for errors
                    if res[0] == -1:
                        raise Exception(res[1])

                    try:
                        job_list.remove(res[1])
                        out_files.append(res[1])
                    except ValueError:
                        self.logger.warning("[%s] Cannot find job %s.", inspect.stack()[0][3], res)

                    # Update progress dialog
                    self.logger.debug("[%s] Got as a result %s.", inspect.stack()[0][3], res)
                    dg.updateProgress.emit(res[0], res[1])

                    # Check is operation was cancelled
                    if dg.wasCancelled():
                        job_queue.empty()
                        files = []

                except Queue.Empty:
                    pass

                except Exception, e:
                    self.logger.error("[%s] Processing failed. Aborting. (Error: %s)", inspect.stack()[0][3], e)
                    dg.close()
                    worker.terminate()
                    return

                if len(job_list) == 0 and len(files) == 0:
                    job_queue.put(None)
                    break

            # Get output
            try:
                (index, out) = res_queue.get(timeout=2)
                # Store results in a model
                model = ResultModel(out, out_files, self)
                self.result_list.setModel(model)
                self.result_list.setItemDelegate(PushButtonDelegate((4, 5), ('View', 'Save'), (model.view_dataset, model.save_dataset)))
                # Setup column width
                self.result_list.resizeColumnsToContents()
                self.result_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
                for i in (4, 5):
                    self.result_list.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Fixed)
                size = self.result_list.fontMetrics().size(QtCore.Qt.TextSingleLine, _trUtf8("View"))
                self.result_list.setColumnWidth(4, size.width() + 20)
                size = self.result_list.fontMetrics().size(QtCore.Qt.TextSingleLine, _trUtf8("Save"))
                self.result_list.setColumnWidth(5, size.width() + 20)

            except Queue.Empty:
                self.logger.error("[%s] Cannot get results from processing.", inspect.stack()[0][3])

            # Join worker process
            worker.join(timeout=2)
            if worker.is_alive():
                self.logger.warning("[%s] Worker join failed. Terminating.")
                worker.terminate()

            # Close dialog
            dg.close()

        else:
            # Bad config file or path
            pass

    @QtCore.pyqtSlot()
    def on_plot_selection_released(self):
        """ Plot selection button slot. """
        # Get selected rows
        model = self.result_list.model()
        rows = list(set([i.row() for i in self.result_list.selectedIndexes()]))
        names = [model._names[r] for r in rows]
        model.view_dataset_multi(names)

    @QtCore.pyqtSlot()
    def on_save_selection_released(self):
        """ Save selection button slot. """
        # Get selected rows
        model = self.result_list.model()
        rows = list(set([i.row() for i in self.result_list.selectedIndexes()]))
        names = [model._names[r] for r in rows]
        model.save_dataset_multi(names)

    @QtCore.pyqtSlot()
    def on_saveall_button_released(self):
        """ Save all button slot. """
        model = self.result_list.model()
        model.save_dataset_multi(model._names)

    @QtCore.pyqtSlot()
    def on_clear_button_released(self):
        """ Clear all button slot. """
        self.result_list.setModel(None)

    @QtCore.pyqtSlot()
    def on_exit_button_released(self):
        """ Close button slot. """
        self.close()

    ##
    ## Close event handler
    ##
    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """ Ask confirmation before closing. """
        ans = QtGui.QMessageBox.question(
                        self,
                        _trUtf8("Confirm close"),
                        _trUtf8("Are you sure you want to close? All unsaved results will be lost."),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
        if ans == QtGui.QMessageBox.Yes:
            # Close all dialogs
            for d in self.dialogs:
                d.close()
            # Shutting down logging server
            self.logserver.server.shutdown()
            self.logserver.join()
            event.accept()
        else:
            event.ignore()

    ##
    ## Timer event to read logs from the OA and update plots
    ##
    @QtCore.pyqtSlot(QtCore.QTimerEvent)
    def timerEvent(self, event):
        """ Handle timer event. """
        if self.logserver.dh.count():
            self.logger.debug("[%s] Updating log. Found %d new entries.", inspect.stack()[0][3], self.logserver.dh.count())
            while True:
                log = self.logserver.dh.pop()
                if log is None:
                    break
                self.error_log.addItem(log)
            self.error_log.sortItems(QtCore.Qt.DescendingOrder)

        # Update plots
        for d in self.dialogs:
            d.refresh_signal.emit(self.result_list.model().fetch_data(d.names))

    ##
    ## Log update slot
    ##
    @QtCore.pyqtSlot(unicode)
    def update_log(self, text):
        """ Update log view. """
        self.error_log.addItem(text)
        self.error_log.sortItems(QtCore.Qt.DescendingOrder)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)