# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Editor - XML configuration handling

Version 2.0

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
import copy
import inspect
import xml.etree.ElementTree as ET

from PyQt4 import QtCore
from PyQt4 import QtGui

from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAEditor")

from OAModels import ConfigTableModel
from OAModels import ConfigParameterModel
from OADelegate import ColumnDelegate

from Ui import Ui_OALoadHDF
from Ui import Ui_OAAddElement


class OAConfiguration(GuiBase):

    """ Manage the configuration file for OA Editor. """

    def __init__(self, parent=None):
        """ Constructor. """
        # Parent constructor
        GuiBase.__init__(self)

        # Store parent object
        self._parent = parent
        self.config = {}
        self._profile = None
        self.main = {}
        self._currentfilename = None

        self.rawtypes = []
        from OACommon import DataObj
        for name in dir(DataObj):
            try:
                if name == 'BaseDataset':
                    continue
                raw = getattr(DataObj, name)
                if not hasattr(raw, '_check_data'):
                    continue
                self.rawtypes.append(name)

            except:
                continue

        self.logger.debug("[%s] Loaded %d raw dataset types.", inspect.stack()[0][3], len(self.rawtypes))

        self.algotypes = {}
        from OACommon import Algorithms
        for name in dir(Algorithms):
            try:
                algo = getattr(Algorithms, name)
                if not hasattr(algo, 'default_configure'):
                    continue

                # Get default parameters
                self.algotypes[name] = algo.default_configure()

                # Get special parameters
                try:
                    customdelegates = algo.configure()
                    for cd in customdelegates:
                        if customdelegates[cd] is None and cd in self.algotypes[name]:
                            del self.algotypes[name][cd]
                        else:
                            self.algotypes[name][cd] = customdelegates[cd]
                except:
                    pass
            except:
                pass

        self.logger.debug("[%s] Loaded %d algorithm types.", inspect.stack()[0][3], len(self.algotypes))

        self.prestypes = {}
        from OACommon import Presenters
        for name in dir(Presenters):
            try:
                pres = getattr(Presenters, name)
                if not hasattr(pres, 'default_configure'):
                    continue

                # Get default parameters
                self.prestypes[name] = pres.default_configure()

                # Get special parameters
                try:
                    customdelegates = pres.configure()
                    for cd in customdelegates:
                        if customdelegates[cd] is None and cd in self.prestypes[name]:
                            del self.prestypes[name][cd]
                        else:
                            self.prestypes[name][cd] = customdelegates[cd]
                except Exception:
                    pass
            except Exception:
                continue

        self.logger.debug("[%s] Loaded %d presenter types.", inspect.stack()[0][3], len(self.prestypes))

    def parent(self):
        """ Return parent object. """
        return self._parent

    def load(self, filename):
        """ Load configuration from given file. """
        try:
            # Parse XML
            tree = ET.parse(str(filename))
            root = tree.getroot()

        except IOError as e:
            self.logger.error("[%s] Cannot open XML configuration file (Error: %s)", inspect.stack()[0][3], e)
            QtGui.QMessageBox.critical(
                    self.parent(),
                    _trUtf8("Error opening configuration file"),
                    _trUtf8("Unable to open the XML configuration file.\nError: %s") % (e, ))
            return False

        except ET.ParseError as e:
            self.logger.error("[%s] Cannot parse XML configuration file (Error: %s)", inspect.stack()[0][3], e)
            QtGui.QMessageBox.critical(
                    self.parent(),
                    _trUtf8("Error parsing XML file"),
                    _trUtf8("Errors found while parsing the XML configuration file.\nError: %s") % (e, ))
            return False

        self.logger.debug("[%s] Successfully loaded '%s'.", inspect.stack()[0][3], filename)

        try:
            # Get main configuration
            self.main = {}
            if root.find('main') is not None:
                for el in root.find('main').findall('parameter'):
                    try:
                        # Get option name
                        n = el.get('name', '')
                        if n == '':
                            # Unnamed options will be ignored
                            continue
                        # Get selection status
                        sel = bool(int(el.get('selected', 0)))
                        # Store value
                        if n not in self.main:
                            self.main[n] = []
                        self.main[n].append([sel, el.text.strip()])

                    except Exception, e:
                        self.logger.error("[%s] Error parsing <main> section (Error: %s)", inspect.stack()[0][3], e)

                # Verify that only one option per type is selected
                for op in self.main:
                    found = False
                    for i in range(len(self.main[op])):
                        if self.main[op][i][0]:
                            if not found:
                                found = True
                            else:
                                self.main[op][i][0] = False

            # Cycle over all profiles
            for profile in root.findall('profile'):

                name = profile.get('name', '')
                if name == '':
                    # Skip unnamed profile
                    continue

                self.config[name] = {}

                # Load output configuration
                self.config[name]['output'] = {}
                for el in profile.findall('output'):
                    try:
                        # Find type
                        tp = el.get('type', '')
                        if tp == '':
                            # Output without a type will be ignored
                            continue

                        # Get parameters
                        self.config[name]['output'][tp] = {}
                        for param in el.findall('parameter'):
                            n = param.get('name', '')
                            if n == '':
                                continue
                            sel = bool(int(param.get('selected', 0)))

                            if n not in self.config[name]['output'][tp]:
                                self.config[name]['output'][tp][n] = []
                            self.config[name]['output'][tp][n].append([sel, param.text.strip()])

                    except Exception, e:
                        self.logger.error("[%s] Error parsing <output> section (Error: %s)", inspect.stack()[0][3], e)
                        continue

                    # Verify that only one value per parameter is selected
                    for out in self.config[name]['output']:
                        for par in self.config[name]['output'][out]:
                            found = False
                            for i in range(len(self.config[name]['output'][out][par])):
                                if self.config[name]['output'][out][par][i][0]:
                                    if not found:
                                        found = True
                                    else:
                                        self.config[name]['output'][out][par][i][0] = False

                # Load raw datasets
                self.config[name]['rawdata'] = []
                for r in profile.findall('rawdata'):
                    try:
                        element = {}

                        # Get name
                        element['name'] = r.get('name', '')
                        if element['name'] == '':
                            continue
                        # Get enable status
                        element['enabled'] = bool(int(r.get('enabled', 0)))
                        # Get dataset type
                        try:
                            element['type'] = r.find('type').text.strip()
                            if element['type'] not in self.rawtypes:
                                raise
                        except:
                            continue
                        # Get HDF5 path
                        try:
                            element['path'] = r.find('path').text.strip()
                        except:
                            element['path'] = ''

                    except Exception, e:
                        self.logger.error("[%s] Error parsing <rawdata> section (Error: %s)", inspect.stack()[0][3], e)
                        continue

                    self.config[name]['rawdata'].append(element)

                self.logger.debug("[%s] Loaded %d raw datasets for profile '%s'.", inspect.stack()[0][3], len(self.config[name]['rawdata']), name)

                # Load algorithms
                self.config[name]['algo'] = []
                for a in profile.findall('algorithm'):
                    try:
                        element = {}

                        # Get name
                        element['name'] = a.get('name', '')
                        if element['name'] == '':
                            continue
                        # Get enable status
                        element['enabled'] = bool(int(a.get('enabled', 0)))
                        # Get alogrithm type
                        try:
                            element['type'] = a.find('type').text.strip()
                            if element['type'] not in self.algotypes:
                                raise
                        except:
                            continue
                        # Get order
                        try:
                            element['order'] = int(a.find('order').text.strip())
                        except:
                            o = 0
                            for temp in self.config[name]['algo']:
                                if temp['order'] > o:
                                    o = temp['order']
                            element['order'] = o + 1
                        # Get parameters
                        element['parameters'] = {}
                        for param in a.findall('parameter'):
                            try:
                                pn = param.get('name', '')
                                if pn == "":
                                    continue
                                try:
                                    tp = param.attrib['type']
                                except:
                                    self.logger.warning("[%s] Cannot find type of parameter '%s', default to 'expr'.", inspect.stack()[0][3], pn)
                                    tp = 'expr'
                                try:
                                    val = param.text.strip()
                                except:
                                    val = ''
                            except Exception, e:
                                self.logger.error("[%s] Error parsing algorithm parameter (Error: %s)", inspect.stack()[0][3], e)
                                continue
                            element['parameters'][pn] = {'type': tp, 'value': val}

                    except Exception, e:
                        self.logger.error("[%s] Error parsing <algorithm> section (Error: %s)", inspect.stack()[0][3], e)
                        continue

                    self.config[name]['algo'].append(element)

                self.logger.debug("[%s] Loaded %d algorithms for profile '%s'.", inspect.stack()[0][3], len(self.config[name]['algo']), name)

                # Load presenters
                self.config[name]['pres'] = []
                for p in profile.findall('presenter'):
                    try:
                        element = {}

                        # Get name
                        element['name'] = p.get('name', '')
                        if element['name'] == '':
                            continue
                        # Get enable status
                        element['enabled'] = bool(int(p.get('enabled', 0)))
                        # Get presenter type
                        try:
                            element['type'] = p.find('type').text.strip()
                            if element['type'] not in self.prestypes:
                                raise
                        except:
                            continue
                        # Get parameters
                        element['parameters'] = {}
                        for param in p.findall('parameter'):
                            try:
                                pn = param.get('name', '')
                                if pn == '':
                                    continue
                                try:
                                    tp = param.attrib['type']
                                except:
                                    self.logger.warning("[%s] Cannot find type of parameter '%s', default to 'expr'.", inspect.stack()[0][3], pn)
                                    tp = 'expr'
                                try:
                                    val = param.text.strip()
                                except:
                                    val = ''
                            except Exception, e:
                                self.logger.error("[%s] Error parsing presenter parameter (Error: %s)", inspect.stack()[0][3], e)
                                continue
                            element['parameters'][pn] = {'type': tp, 'value': val}
                        # Get filters
                        element['filters'] = []
                        for fil in p.findall('filter'):
                            try:
                                try:
                                    val = fil.text.strip()
                                except:
                                    val = ''
                                element['filters'].append({
                                                            'enabled': bool(int(fil.get('enabled', 0))),
                                                            'target': fil.get('target', ''),
                                                            'type': fil.get('type', 'eq'),
                                                            'operator': fil.get('operator', 'and'),
                                                            'value': val
                                                          })
                            except Exception, e:
                                self.logger.error("[%s] Error parsing filter (Error: %s)", inspect.stack()[0][3], e)

                    except Exception, e:
                        self.logger.error("[%s] Error parsing <presenter> section (Error: %s)", inspect.stack()[0][3], e)
                        continue

                    self.config[name]['pres'].append(element)

                self.logger.debug("[%s] Loaded %d presenters for profile '%s'.", inspect.stack()[0][3], len(self.config[name]['pres']), name)

            if len(self.config) > 0:
                self._currentfilename = filename
            else:
                self._currentfilename = None
            return True

        except Exception, e:
            self.logger.error("[%s] Unexpected error while loading configuration (Error: %s)", inspect.stack()[0][3], e, exc_info=True)
            self.config = {}
            self.main = {}
            self._profile = None
            self._currentfilename = None
            return False

    def _buildxml(self):
        """ Build XML configuration tree. """
        # Create new root
        root = ET.Element('configuration')

        # Main configuration
        main = ET.Element('main')
        for m in self.main:
            for opt in self.main[m]:
                el = ET.Element('parameter', {'name': m, 'selected': str(int(opt[0]))})
                el.text = opt[1]
                main.append(el)
        root.append(main)

        for profile in self.config:
            prof_el = ET.Element('profile', {'name': profile})

            # Output configuration
            for o in self.config[profile]['output']:
                # Output element
                out = ET.Element('output', {'type': o})
                # Paremeters
                for par in self.config[profile]['output'][o]:
                    for opt in self.config[profile]['output'][o][par]:
                        el = ET.Element('parameter', {'name': par, 'selected': str(int(opt[0]))})
                        el.text = opt[1]
                        out.append(el)
                prof_el.append(out)

            # Raw datasets
            for r in self.config[profile]['rawdata']:
                raw = ET.Element('rawdata', {'name': r['name'], 'enabled': str(int(r['enabled']))})
                # Type
                tp = ET.Element('type')
                tp.text = r['type']
                raw.append(tp)
                # Path
                path = ET.Element('path')
                path.text = r['path']
                raw.append(path)
                prof_el.append(raw)

            # Algorithms
            for a in self.config[profile]['algo']:
                algo = ET.Element('algorithm', {'name': a['name'], 'enabled': str(int(a['enabled']))})
                # Type
                tp = ET.Element('type')
                tp.text = a['type']
                algo.append(tp)
                # Order
                order = ET.Element('order')
                order.text = str(a['order'])
                algo.append(order)
                # Parameters
                for par in a['parameters']:
                    el = ET.Element('parameter', {'name': par, 'type': a['parameters'][par]['type']})
                    if type(a['parameters'][par]['value']) is bool:
                        el.text = str(int(a['parameters'][par]['value']))
                    else:
                        el.text = str(a['parameters'][par]['value'])
                    algo.append(el)

                prof_el.append(algo)

            # Presenters
            for p in self.config[profile]['pres']:
                pres = ET.Element('presenter', {'name': p['name'], 'enabled': str(int(p['enabled']))})
                # Type
                tp = ET.Element('type')
                tp.text = p['type']
                pres.append(tp)
                # Parameters
                for par in p['parameters']:
                    el = ET.Element('parameter', {'name': par, 'type': p['parameters'][par]['type']})
                    if type(p['parameters'][par]['value']) is bool:
                        el.text = str(int(p['parameters'][par]['value']))
                    else:
                        el.text = str(p['parameters'][par]['value'])
                    pres.append(el)
                # Filters
                for fil in p['filters']:
                    el = ET.Element('filter', {'enabled': str(int(fil['enabled'])), 'operator': fil['operator'], 'target': fil['target'], 'type': fil['type']})
                    el.text = fil['value']
                    pres.append(el)

                prof_el.append(pres)

            # Add profile
            root.append(prof_el)

        # Pretty indentation
        self._indent(root)
        return root

    def verify(self):
        """ Verify the consistency of the currently enabled elements. """
        # Output list of inconsistencies
        out = {}

        # Get references to current configuration
        presenters = self.config[self._profile]['pres']
        algorithms = self.config[self._profile]['algo']
        rawdata = self.config[self._profile]['rawdata']

        # Cycle over all presenters
        for i in range(len(presenters)):
            # Check if the presenter is enabled
            if presenters[i]['enabled']:
                # Get presenter input variables
                invar = self.getPresInVars(i)

                # For each variable search the source algo and check that is enabled
                for var in invar:
                    for j in range(len(algorithms)):
                        # Get output variables
                        outvar = self.getAlgoOutVars(j)
                        if var not in outvar:
                            continue
                        else:
                            # Found!
                            if not algorithms[j]['enabled']:
                                # Algo is disabled
                                # Add pres i depend on algo j
                                if "a_%d" % (j, ) in out:
                                    out["a_%d" % (j, )].append(('p', i))
                                else:
                                    out["a_%d" % (j, )] = [('p', i)]
                                break
                            else:
                                # Algo is enabled, nothing to do. Algo deps will
                                # be checked in the next step.
                                break

                    else:
                        # Variable not found
                        # Add pres i depends on missing variable
                        if "v_%s" % (var, ) in out:
                            out["v_%s" % (var, )].append(('p', i))
                        else:
                            out["v_%s" % (var, )] = [('p', i)]

                # Search filter targets
                for k in range(len(presenters[i]['filters'])):
                    for j in range(len(algorithms)):
                        # Get output variables
                        outvar = self.getAlgoOutVars(j)
                        if presenters[i]['filters'][k]['target'] not in outvar:
                            continue
                        else:
                            # Found!
                            if not algorithms[j]['enabled']:
                                # Algo is disabled
                                # Add pres i depend on algo j
                                if "a_%d" % (j, ) in out:
                                    out["a_%d" % (j, )].append(('f', i, k))
                                else:
                                    out["a_%d" % (j, )] = [('f', i, k)]
                                break
                            else:
                                # Algo is enabled, nothing to do. Algo deps will
                                # be checked in the next step.
                                break

                    else:
                        # Variable not found
                        # Add pres i depends on missing variable
                        if "v_%s" % (var, ) in out:
                            out["v_%s" % (var, )].append(('f', i, k))
                        else:
                            out["v_%s" % (var, )] = [('f', i, k)]

        # Cycle over all algorithms
        for i in range(len(algorithms)):
            # Check if the algo is enabled
            if algorithms[i]['enabled']:
                # Get algo input variables
                invar = self.getAlgoInVars(i)
                # For each variable search the source algo or raw dataset
                for var in invar:
                    for j in range(len(algorithms)):
                        # Get output variables
                        outvar = self.getAlgoOutVars(j)
                        if var not in outvar:
                            # Not found
                            continue
                        else:
                            # Variable found
                            if not algorithms[j]['enabled']:
                                # Algo is disabled
                                # Add algo i depends on algo j
                                if "a_%d" % (j, ) in out:
                                    out["a_%d" % (j, )].append(('a', i))
                                else:
                                    out["a_%d" % (j, )] = [('a', i)]
                                break
                            else:
                                # Algo enabled, check order
                                if algorithms[j]['order'] > algorithms[i]['order']:
                                    # Wrong order
                                    # Bad ordering of algo i and j
                                    if "o_%d" % (j, ) in out:
                                        out["o_%d" % (j, )].append(('a', i))
                                    else:
                                        out["o_%d" % (j, )] = [('a', i)]
                                    break
                                else:
                                    # Order ok, nothing to do
                                    break
                    else:
                        # Var not found in algo, search raw datasets
                        for j in range(len(rawdata)):
                            if var != rawdata[j]['name']:
                                # Not found
                                continue
                            else:
                                # Found!
                                if not rawdata[j]['enabled']:
                                    # Raw data disabled
                                    # Add algo i depends on rawdata j
                                    if "r_%d" % (j, ) in out:
                                        out["r_%d" % (j, )].append(('a', i))
                                    else:
                                        out["r_%d" % (j, )] = [('a', i)]
                                    break
                                else:
                                    # Raw data enabled, nothing to do
                                    break
                        else:
                            # Variable not found
                            # Add algo i depends on missing variable
                            if "v_%s" % (var, ) in out:
                                out["v_%s" % (var, )].append(('a', i))
                            else:
                                out["v_%s" % (var, )] = [('a', i)]

        return out

    def resortAlgoOrder(self):
        """ Resort the algorithm order to handle their dependencies. """
        # Get all algo I/O
        algolist = []
        for i in range(len(self.config[self._profile]['algo'])):
            algolist.append({'in': self.getAlgoInVars(i), 'out': self.getAlgoOutVars(i)})

        # Search dependencies
        deps = {}
        for i in range(len(algolist)):
            deps[i] = set()
            for v in algolist[i]['in']:
                for j in range(len(algolist)):
                    if i == j:
                        continue
                    if v in algolist[j]['out']:
                        deps[i].add(j)

        #nodeps = reduce(set.union, deps.itervalues()) - set(data.iterkeys())
        out = []
        while True:
            ordered = set(item for item, dep in deps.iteritems() if not dep)
            if not ordered:
                break
            out.append(ordered)
            deps = {item: (dep - ordered) for item, dep in deps.iteritems() if item not in ordered}
        if len(deps) > 0:
            self.logger.debug("[%s] Cyclic dependency between items '%s'", inspect.stack()[0][3], "', '".join(repr(x) for x in deps.iteritems()))
        else:
            for level in out:
                self.logger.debug("[%s] New order: '%s'", inspect.stack()[0][3], "', '".join(self.config[self._profile]['algo'][x]['name'] for x in level))

        # Resort algos
        order = 0
        for level in out:
            for i in level:
                self.config[self._profile]['algo'][i]['order'] = order
                order += 1

    def save(self):
        """ Save modification to the currently loaded file. """
        if self._currentfilename is None:
            return False

        root = self._buildxml()
        tree = ET.ElementTree(root)

        try:
            self.logger.info("[%s] Saving configuration to %s. ", inspect.stack()[0][3], self._currentfilename)
            tree.write(self._currentfilename)

        except Exception, e:
            QtGui.QMessageBox.critical(
                    self.parent(),
                    _trUtf8("Generation error"),
                    _trUtf8("There was an error generating the configuration file. The file might have been corrupted.\nError was: %s") % (e, ))

    def saveas(self):
        """ Save modifications to a new file. Open a dialog to ask for
        filename. """
         # Call file dialog
        name = unicode(QtGui.QFileDialog.getSaveFileName(
                            self.parent(),
                            _trUtf8("Save as..."),
                            os.getcwd(),
                            _trUtf8("Configuration file (*.xml)")))
        if(name != ""):
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

            root = self._buildxml()
            tree = ET.ElementTree(root)

            try:
                self.logger.info("[%s] Saving configuration to %s. ", inspect.stack()[0][3], name)
                tree.write(name)

            except Exception, e:
                QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8("Generation error"),
                        _trUtf8("There was an error generating the configuration file. The file might have been corrupted.\nError was: %s") % (e, ))

    def generate(self, filename):
        """ Generate a new configuration file for the OA server. """

        # Check if a profile si selected
        if self._profile is None:
            QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8("Generation error"),
                        _trUtf8("You must select or create a profile before you can generate an output file."))
            return False

        # Check if a profile si selected
        if len(self.parent().config_errors) > 0:
            QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8("Generation error"),
                        _trUtf8("You must resolve conflicts before generating the configuration file."))
            return False

        # Create new root
        root = ET.Element('configuration')

        try:
            # Create OA processing output
            for tp in ('oa', 'present'):
                out = ET.Element('output', {'type': tp})
                mod = ET.Element('module')
                cl = ET.Element('class')
                for par, val in self.config[self._profile]['output'][tp].iteritems():
                    if par == 'module':
                        for p in val:
                            if p[0]:
                                mod.text = p[1]
                    elif par == 'class':
                        for p in val:
                            if p[0]:
                                cl.text = p[1]
                    else:
                        for p in val:
                            if p[0]:
                                el = ET.Element('parameter', {'name': par})
                                el.text = p[1]
                                out.append(el)

                out.append(mod)
                out.append(cl)
                root.append(out)

            # Add raw datasets
            for r in self.config[self._profile]['rawdata']:
                if r['enabled']:
                    el = ET.Element('rawdata', {'name': r['name']})
                    tp = ET.Element('type')
                    tp.text = r['type']
                    path = ET.Element('path')
                    path.text = r['path']
                    el.append(tp)
                    el.append(path)
                    root.append(el)

            # Add algorithms
            for a in self.config[self._profile]['algo']:
                if a['enabled']:
                    algo = ET.Element('algorithm', {'name': a['name']})
                    # Type
                    tp = ET.Element('type')
                    tp.text = a['type']
                    algo.append(tp)
                    # Order
                    order = ET.Element('order')
                    order.text = str(a['order'])
                    algo.append(order)
                    # Create model to check data type of parameters
                    model = ConfigParameterModel(a['parameters'], self.algotypes[a['type']], self.config[self._profile]['algo'].index(a), self._parent)
                    # Cycle over parameters
                    for i in range(model.rowCount()):
                        # Get model name
                        par = model._names[i]
                        # If value is empty and parameter is not mandatory, just skip
                        if a['parameters'][par]['value'] == "":
                            if not model._config[par]['mandatory']:
                                continue
                            else:
                                raise Exception("Parameter '%s' of algorithm '%s' is mandatory." % (par, a['name']))
                        # Check data type
                        (dt, ok) = model._checkDType(i, QtCore.QVariant(a['parameters'][par]['value']))
                        if not ok:
                            if not model._config[par]['mandatory']:
                                # Parameter is not mandatory and can be skipped
                                continue
                            else:
                                raise Exception("Parameter '%s' of algorithm '%s' is missing or has a wrong value." % (par, a['name']))
                        else:
                            # Parameter is ok
                            el = ET.Element('parameter', {'name': par, 'type': a['parameters'][par]['type']})
                            if type(a['parameters'][par]['value']) is bool:
                                el.text = str(int(a['parameters'][par]['value']))
                            else:
                                el.text = str(a['parameters'][par]['value'])
                            algo.append(el)
                    root.append(algo)

            # Add presenters
            for p in self.config[self._profile]['pres']:
                if p['enabled']:
                    pres = ET.Element('presenter', {'name': p['name']})
                    # Type
                    tp = ET.Element('type')
                    tp.text = p['type']
                    pres.append(tp)
                    # Create model to check data type of parameters
                    model = ConfigParameterModel(p['parameters'], self.prestypes[p['type']], self.config[self._profile]['pres'].index(p), self._parent)
                    # Cycle over parameters
                    for i in range(model.rowCount()):
                        # Get model name
                        par = model._names[i]
                        # If value is empty and parameter is not mandatory, just skip
                        if p['parameters'][par]['value'] == "":
                            if not model._config[par]['mandatory']:
                                continue
                            else:
                                raise Exception("Parameter '%s' of presenter '%s' is mandatory." % (par, p['name']))
                        # Check data type
                        (dt, ok) = model._checkDType(i, QtCore.QVariant(p['parameters'][par]['value']))
                        if not ok:
                            if not model._config[par]['mandatory']:
                                # Parameter is not mandatory and can be skipped
                                continue
                            else:
                                raise Exception("Parameter '%s' of presenter '%s' is missing or has a wrong value." % (par, p['name']))
                        else:
                            # Parameter is ok
                            el = ET.Element('parameter', {'name': par, 'type': p['parameters'][par]['type']})
                            if type(p['parameters'][par]['value']) is bool:
                                el.text = str(int(p['parameters'][par]['value']))
                            else:
                                el.text = str(p['parameters'][par]['value'])
                            pres.append(el)
                    # Filters
                    for fil in p['filters']:
                        if fil['enabled']:
                            if fil['target'] == "":
                                raise Exception("Filter of presenter '%s' is missing the target." % (p['name'], ))
                            if fil['value'] == "":
                                raise Exception("Filter of presenter '%s' is missing a value." % (p['name'], ))
                            # TODO: add a check that the current target is valid
                            el = ET.Element('filter', {'operator': fil['operator'], 'target': fil['target'], 'type': fil['type']})
                            el.text = fil['value']
                            pres.append(el)
                    root.append(pres)

        except AssertionError, e:
            pass

        except Exception, e:
            QtGui.QMessageBox.critical(
                    self.parent(),
                    _trUtf8("Generation error"),
                    _trUtf8("There was an error generating the output file.\nError was: %s") % (e, ))
            self.logger.error("[%s] Generation error (Error: %s)", inspect.stack()[0][3], e)
            return False

        # Build tree
        self._indent(root)
        tree = ET.ElementTree(root)

        try:
            self.logger.info("[%s] Saving output file to %s. ", inspect.stack()[0][3], filename)
            tree.write(filename)
            return True

        except Exception, e:
            QtGui.QMessageBox.critical(
                    self.parent(),
                    _trUtf8("Generation error"),
                    _trUtf8("There was an error generating the output file. The file might have been corrupted.\nError was: %s") % (e, ))
            return False

    def raw_from_h5(self):
        """ Load raw data definitions from a given HDF5 file. """

        # First try to import H5PY
        try:
            import h5py as h5
        except Exception, e:
            QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8("Import error"),
                        _trUtf8("There was an error importing the H5PY module. The module is not installed or might have been corrupted. \nError was: %s") % (e, ))
            return False

        # Then try to import NumPy
        try:
            import numpy as np
        except Exception, e:
            QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8("Import error"),
                        _trUtf8("There was an error importing the NumPy module. The module is not installed or might have been corrupted. \nError was: %s") % (e, ))
            return False

        # Check if a profile is selected
        if self._profile is None:
            QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8("Profile error"),
                        _trUtf8("You must select or create a profile before trying to add raw datasets."))
            return False

        # Ask for filename
        filename = QtGui.QFileDialog.getOpenFileName(
                        self.parent(),
                        _trUtf8(u"Open HDF5 file"),
                        os.getcwd(),
                        _trUtf8(u"HDF5 files (*.h5 *.hdf5)"))

        self.logger.debug("[%s] Selected file '%s'.", inspect.stack()[0][3], filename)

        # Open HDF5 file
        try:
            f = h5.File(str(filename), 'r')
        except Exception, e:
            QtGui.QMessageBox.critical(
                        self.parent(),
                        _trUtf8(u"Error loading file"),
                        _trUtf8(u"There was an error trying to open file '%s'\nError was: %s") % (filename, e))
            return False
        else:
            self.logger.debug("[%s] Successfully opened file '%s'.", inspect.stack()[0][3], filename)

        # Function to inspect a group
        def dump_element(el, path):
            new_items = []
            for item in el.items():
                if type(item[1]) is h5.Group:
                    # Found group. Iterate!
                    self.logger.debug("[%s] Found group '%s' with %d items.", inspect.stack()[0][3], path + item[0], len(item[1].items()))
                    new_items += dump_element(item[1], path + item[0] + '/')

                elif type(item[1]) is h5.Dataset:
                    # Found dataset
                    if type(item[1].value) == np.ndarray and len(item[1].value.shape) <= 3:
                        if len(item[1].value.shape) == 1:
                            etype = "Scalar"
                        elif len(item[1].value.shape) == 2:
                            etype = "Array"
                        elif len(item[1].value.shape) == 3:
                            etype = "Image"
                        else:
                            self.logger.warning("[%s] Impossible to recognize type of dataset '%s' with shape %s.", inspect.stack()[0][3], path + item[0], item[1].value.shape)
                            continue
                        self.logger.debug("[%s] Dataset '%s' was identified as '%s'.", inspect.stack()[0][3], path + item[0], etype)
                        new_items.append(dict(name=item[0], type=etype, path=path + item[0], enabled=False))

                    else:
                        # Metadata
                        if type(item[1].value) in (int, long, float, np.float64, np.float32, np.int64, np.uint64, np.int32, np.uint32, np.int16, np.uint16, np.int8, np.uint8):
                            self.logger.debug("[%s] Dataset '%s' was identified as 'Metadata'.", inspect.stack()[0][3], path + item[0])
                            new_items.append(dict(name=item[0], type="Metadata", path=path + item[0], enabled=False))
                else:
                    self.logger.warning("[%s] Ignoring unknown element '%s' (Type: %s)", inspect.stack()[0][3], path + item[0], type(item[1]))
            return new_items

        # Dump HDF5 content recursively
        datasets = dump_element(f, '')

        # Call dialog
        dg = OALoadHDF(datasets, self.parent())
        ret = dg.exec_()

        if ret == QtGui.QDialog.Accepted:
            if dg.clearall:
                # Replace
                self.logger.debug("[%s] Replacing raw datasets with selected ones.", inspect.stack()[0][3])
                self.config[self._profile]['rawdata'] = []
                for d in dg.datasets:
                    if d['enabled']:
                        d['enabled'] = False
                        self.config[self._profile]['rawdata'].append(d)
                return True

            else:
                # Append
                self.logger.debug("[%s] Appending selected raw datasets.", inspect.stack()[0][3])
                added = False
                for d in dg.datasets:
                    if d['enabled']:
                        newname = d['name']

                        while(True):
                            # Search for a dataset with the same name
                            found = False
                            for old in self.config[self._profile]['rawdata']:
                                if newname == old['name']:
                                    found = True

                            if found:
                                (newname, ok) = QtGui.QInputDialog.getText(
                                                        self.parent(),
                                                        _trUtf8("Duplicate name"),
                                                        _trUtf8("The selected name is already in use. Please choose another one or press Cancel to skip"),
                                                        QtGui.QLineEdit.Normal,
                                                        newname)
                                if not ok:
                                    break
                            else:
                                d['name'] = newname
                                d['enabled'] = False
                                self.config[self._profile]['rawdata'].append(d)
                                added = True
                                break
                return added

        else:
            self.logger.debug("[%s] Operation aborted.", inspect.stack()[0][3])
            return False

    def profiles(self):
        """ Return the list of currently available profiles. """
        return sorted(self.config.keys())

    def currentProfile(self):
        """ Return the current profile name. """
        return self._profile

    def setCurrentProfile(self, profile):
        """ Set the current profile. """
        if profile in self.config:
            self._profile = profile
        else:
            QtGui.QMessageBox.critical(
                    self.parent(),
                    _trUtf8("Non-existent profile"),
                    _trUtf8("The selected profile does not exist."))
            self.logger.error("[%s] Selected non-existent profile '%s'.", inspect.stack()[0][3], profile)

    def addProfile(self):
        """ Add a new profile. """
        name = u""

        while(True):
            (name, ok) = QtGui.QInputDialog.getText(
                                self.parent(),
                                _trUtf8("Profile name"),
                                _trUtf8("Insert new profile name:"),
                                QtGui.QLineEdit.Normal,
                                name)
            name = unicode(name)
            if not ok or name == "":
                return ("", False)
            if name not in self.config:
                # Add profile
                self.config[name] = {}
                self.config[name]['output'] = {}
                self.config[name]['rawdata'] = []
                self.config[name]['algo'] = []
                self.config[name]['pres'] = []
                return (name, True)
            else:
                QtGui.QMessageBox.warning(
                        self.parent(),
                        _trUtf8("Duplicate name"),
                        _trUtf8("The selected name is already in use."))

    def deleteProfile(self, name):
        """ Delete the given profile. """
        if name in self.config:
            ans = QtGui.QMessageBox.question(
                        self.parent(),
                        _trUtf8("Confirm deletion"),
                        _trUtf8("Are you sure to delete the profile '%s'?") % (name, ),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
            if ans == QtGui.QMessageBox.Yes:
                del self.config[name]
                return True
        return False

    def renameProfile(self, current_name):
        """ Rename a profile. """
        if current_name in self.config:
            name = current_name
            while(True):
                (name, ok) = QtGui.QInputDialog.getText(
                                    self.parent(),
                                    _trUtf8("Profile name"),
                                    _trUtf8("Insert new profile name:"),
                                    QtGui.QLineEdit.Normal,
                                    name)
                name = unicode(name)
                if not ok or name == "":
                    return ("", False)
                if name == current_name:
                    return ("", False)
                if name not in self.config:
                    self.config[name] = self.config[current_name]
                    del self.config[current_name]
                    return (name, True)
                else:
                    QtGui.QMessageBox.warning(
                            self.parent(),
                            _trUtf8("Duplicate name"),
                            _trUtf8("The selected name is already in use."))

    def duplicateProfile(self, current_name):
        """ Rename a profile. """
        if current_name in self.config:
            name = current_name
            while(True):
                (name, ok) = QtGui.QInputDialog.getText(
                                    self.parent(),
                                    _trUtf8("Profile name"),
                                    _trUtf8("Insert new profile name:"),
                                    QtGui.QLineEdit.Normal,
                                    name)
                name = unicode(name)
                if not ok or name == "":
                    return ("", False)
                if name not in self.config:
                    self.config[name] = copy.deepcopy(self.config[current_name])
                    return (name, True)
                else:
                    QtGui.QMessageBox.warning(
                            self.parent(),
                            _trUtf8("Duplicate name"),
                            _trUtf8("The selected name is already in use."))

    def getAlgoOutVars(self, index=None):
        """ Return algorithm output variables. """
        if index is None:
            indexes = range(len(self.config[self._profile]['algo']))
        else:
            indexes = [index]
        out = []
        for i in indexes:
            for p in self.config[self._profile]['algo'][i]['parameters']:
                if self.config[self._profile]['algo'][i]['parameters'][p]['type'] == 'outvar':
                    try:
                        var = eval(self.config[self._profile]['algo'][i]['parameters'][p]['value'], {"__builtins__": None}, {})
                        if type(var) is list:
                            out += var
                        else:
                            pass
                    except NameError:
                        out.append(self.config[self._profile]['algo'][i]['parameters'][p]['value'])
                    except Exception:
                        pass
        return out

    def getAlgoInVars(self, index=None):
        """ Return algorithm input variables. """
        if index is None:
            indexes = range(len(self.config[self._profile]['algo']))
        else:
            indexes = [index]
        out = []
        for i in indexes:
            for p in self.config[self._profile]['algo'][i]['parameters']:
                if self.config[self._profile]['algo'][i]['parameters'][p]['type'] == 'var':
                    try:
                        var = eval(self.config[self._profile]['algo'][i]['parameters'][p]['value'], {"__builtins__": None}, {})
                        if type(var) is list:
                            out += var
                        else:
                            pass
                    except NameError:
                        out.append(self.config[self._profile]['algo'][i]['parameters'][p]['value'])
                    except Exception:
                        pass
        return out

    def getPresOutVars(self, index=None):
        """ Return algorithm output variables. """
        if index is None:
            indexes = range(len(self.config[self._profile]['pres']))
        else:
            indexes = [index]
        out = []
        for i in indexes:
            for p in self.config[self._profile]['pres'][i]['parameters']:
                if self.config[self._profile]['pres'][i]['parameters'][p]['type'] == 'tango':
                    try:
                        var = eval(self.config[self._profile]['pres'][i]['parameters'][p]['value'], {"__builtins__": None}, {})
                        if type(var) is list:
                            out += var
                        else:
                            pass
                    except NameError:
                        out.append(self.config[self._profile]['pres'][i]['parameters'][p]['value'])
                    except Exception:
                        pass
        return out

    def getPresInVars(self, index=None):
        """ Return algorithm input variables. """
        if index is None:
            indexes = range(len(self.config[self._profile]['pres']))
        else:
            indexes = [index]
        out = []
        for i in indexes:
            for p in self.config[self._profile]['pres'][i]['parameters']:
                if self.config[self._profile]['pres'][i]['parameters'][p]['type'] == 'var':
                    try:
                        var = eval(self.config[self._profile]['pres'][i]['parameters'][p]['value'], {"__builtins__": None}, {})
                        if type(var) is list:
                            out += var
                        else:
                            pass
                    except NameError:
                        out.append(self.config[self._profile]['pres'][i]['parameters'][p]['value'])
                    except Exception:
                        pass
        return out

    def getRawDatasets(self, index=None):
        """ Return raw dataset names. """
        if index is None:
            indexes = range(len(self.config[self._profile]['rawdata']))
        else:
            indexes = [index]
        out = []
        for i in indexes:
            out.append(self.config[self._profile]['rawdata'][i]['name'])
        return out

    def getAllVars(self):
        """ Return all the currently defined variables. Raw datasets and
        algo outputs. """
        return sorted(list(set(self.getRawDatasets() + self.getAlgoOutVars())))

    def checkUniqueAlgo(self, index, name):
        """ Check that the given variable is not used by other algorithms. """
        for i in range(len(self.config[self._profile]['algo'])):
            if i == index:
                continue
            values = self.getAlgoOutVars(i)
            if name in values:
                return False
        if name in self.getRawDatasets():
            return False
        return True

    def checkUniquePres(self, index, name):
        """ Check that the given variable is not used by other presenters. """
        for i in range(len(self.config[self._profile]['pres'])):
            if i == index:
                continue
            values = self.getPresOutVars(i)
            if name in values:
                return False
        return True

    def __len__(self):
        return 5

    def __getitem__(self, key):
        if key == 'main':
            return self.main
        if not self._profile:
            raise IndexError('No profile selected.')
        if key not in ['output', 'rawdata', 'algo', 'pres']:
            raise KeyError(key)
        return self.config[self._profile][key]

    def _indent(self, elem, level=0):
        """ Pretty indentation for xml file. """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class OALoadHDF(QtGui.QDialog, Ui_OALoadHDF):

    """ Dialog to select which dataset to load from a HDF5 file. """

    def __init__(self, source, parent=None):
        """ Constructor. """
        # Parent constructor
        QtGui.QDialog.__init__(self, parent)

        # Setup UI
        self.setupUi(self)

        # Build model source
        self.datasets = source

        # Configuration
        delegates = [
            {'column': 1, 'type': 'NullDelegate'},
            {'column': 2, 'type': 'NullDelegate'},
            {'column': 3, 'type': 'CheckboxDelegate'}
        ]

        columns = [
            {'name': 'Name', 'id': 'name', 'unique': True, 'dtype': unicode},
            {'name': 'Type', 'id': 'type', 'unique': False, 'dtype': unicode},
            {'name': 'Path', 'id': 'path', 'unique': False, 'dtype': unicode},
            {'name': '', 'id': 'enabled', 'unique': False, 'dtype': bool}
        ]

        # Create model
        model = ConfigTableModel(self.datasets, columns, self)
        # Create proxy sorter
        sorter = QtGui.QSortFilterProxyModel(self)
        sorter.setSourceModel(model)
        sorter.setDynamicSortFilter(True)
        sorter.sort(0)
        # Set model in TableView
        self.dataset_list.setModel(sorter)
        # Create item delegate
        delegate = ColumnDelegate(delegates, self)
        self.dataset_list.setItemDelegate(delegate)
        # Setup column witdh
        self.dataset_list.resizeColumnsToContents()
        self.dataset_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.dataset_list.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.dataset_list.horizontalHeader().resizeSection(1, 100)
        self.dataset_list.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.dataset_list.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.dataset_list.horizontalHeader().resizeSection(3, 50)
        # Hide vertical header
        self.dataset_list.verticalHeader().hide()
        # Set edit triggers
        self.dataset_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.dataset_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.dataset_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def on_replace_released(self):
        """ Replace button slot. """
        self.clearall = True
        self.accept()

    def on_append_released(self):
        """ Append button slot. """
        self.clearall = False
        self.accept()

    def on_cancel_released(self):
        """ Cancel button slot. """
        self.reject()

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """ Reject modifications if the window is close. """
        self.reject()


class AddDialog(QtGui.QDialog, Ui_OAAddElement):

    """ Dialog to add a new element. """

    def __init__(self, element, types, parent=None):
        """ Constructor. """
        # Parent constructor
        QtGui.QDialog.__init__(self, parent)

        # Setup UI
        self.setupUi(self)

        # Update title and message
        self.message.setText(unicode(self.message.text()) % (element,))
        self.setWindowTitle(unicode(self.windowTitle()) % (element, ))

        # Add types
        self.type.addItems(types)

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """ Reject modifications if the window is close. """
        self.reject()