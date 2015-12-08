# -*- coding: utf-8 -*-

"""
Online Analysis - XML configuration handling

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

import xml.etree.ElementTree as ET
from BaseObject import BaseObject


class Configuration(BaseObject):

    """ Load and store the OA configuration

    Parse the XML configuration file and return a configuration object for
    the OA.

    """

    def __init__(self, xmlfile):
        """ Constructor. Load and parse the XML file. """
        super(Configuration, self).__init__()
        self.name("Configuration")
        self.version("1.0")

        # Configuration storage
        self.output = {}
        self.rawdata = {}
        self.algorithms = []
        self.presenters = []

        # Load XML file with ETree
        try:
            tree = ET.parse(xmlfile)
            root = tree.getroot()
        except IOError as e:
            self.logger.critical("[%s] Cannot open XML configuration file (Error: %s)", self.name(), e)
            return
        except ET.ParseError as e:
            self.logger.critical("[%s] Cannot parse XML configuration file (Error: %s)", self.name(), e)
            return

        # Read output configuration
        try:
            for o in root.findall("output"):
                self.output[o.attrib['type']] = {}
                self.output[o.attrib['type']]['module'] = o.find('module').text.strip()
                self.output[o.attrib['type']]['class'] = o.find('class').text.strip()
                partag = o.findall('parameter')
                params = {}
                for p in partag:
                    params[p.attrib['name']] = p.text.strip()
                self.output[o.attrib['type']]['parameters'] = params

        except Exception as e:
            self.logger.error("[%s] Error parsing output configuration (Error: %s)", self.name(), e)

        # Read raw data configuration
        try:
            for r in root.findall("rawdata"):
                self.rawdata[r.attrib['name']] = (r.find('type').text.strip(), r.find('path').text.strip())
        except Exception as e:
            self.logger.error("[%s] Error parsing raw data configuration (Error: %s)", self.name(), e)

        # Read algorithm configuration
        try:
            import Algorithms
            for algo in root.findall('algorithm'):

                # Get algorithm type
                try:
                    atype = algo.find('type').text.strip()
                except AttributeError:
                    self.logger.error("[%s] No type found in algorithm definition. Skipping.", self.name())
                    continue

                # Get algorith order
                try:
                    order = int(algo.find('order').text.strip())
                except AttributeError:
                    order = None

                # Get algorithm parameters
                params = {}
                try:
                    for p in algo.findall('parameter'):
                        try:
                            # Extract all relevant parameter info
                            n = p.attrib['name']
                            t = p.attrib['type']
                            v = p.text.strip()
                        except Exception, e:
                            # Skip in case of error
                            self.logger.debug("[%s] Skipping parameter (Error: %s)", self.name(), e)
                            continue
                        # Add parameter
                        params[n] = {'type': t, 'value': v}

                except Exception as e:
                    self.logger.error("[%s] Got error while parsing parameters of algorithm '%s' (Error: %s)", self.name(), atype, e)

                # Create algorithm instance
                try:
                    obj = getattr(Algorithms, atype)(params)
                    self.algorithms.append((order, algo.attrib['name'], obj))
                except Exception, e:
                    self.logger.error("[%s] Error creating algorithm of type '%s' (Error: %s)", self.name(), atype, e)
                    continue
            self.algorithms.sort()

        except Exception as e:
            self.logger.error("[%s] Error parsing algorithms configuration (Error: %s)", self.name(), e, exc_info=True)

        # Read presenter configuration
        try:
            import Presenters
            from Filter import Filter

            for pres in root.findall('presenter'):

                # Get presenter type
                try:
                    ptype = pres.find('type').text.strip()
                except AttributeError:
                    self.logger.error("[%s] No type found in presenter definition. Skipping.", self.name())
                    continue

                # Get presenter parameters
                params = {}
                try:
                    for p in pres.findall('parameter'):
                        try:
                            # Extract all relevant parameter info
                            n = p.attrib['name']
                            t = p.attrib['type']
                            v = p.text.strip()
                        except Exception, e:
                            # Skip in case of error
                            self.logger.debug("[%s] Skipping parameter (Error: %s)", self.name(), e)
                            continue
                        # Add parameter
                        params[n] = {'type': t, 'value': v}

                except Exception as e:
                    self.logger.error("[%s] Got error while parsing parameters of presenter '%s' (Error: %s)", self.name(), ptype, e)

                # Get presenter filters
                filters = []
                for f in pres.findall('filter'):
                    try:
                        filters.append(dict(target=f.attrib['target'], type=f.attrib['type'], operator='and', value=f.text.strip()))
                    except Exception, e:
                        self.logger.warning("[%s] Discarding bad filter definition (Error: %s)", self.name(), e)
                        continue
                    try:
                        filters[-1]['operator'] = f.attrib['operator']
                    except:
                        pass

                # Add presenter
                try:
                    obj = getattr(Presenters, ptype)(params, Filter(filters))
                    self.presenters.append((pres.attrib['name'], obj))
                except Exception, e:
                    self.logger.error("[%s] Error creating presenter of type '%s' (Error: %s)", self.name(), ptype, e)
                    continue

        except Exception as e:
            self.logger.error("[%s] Error parsing presenters configuration (Error: %s)", self.name(), e, exc_info=True)

        self.logger.debug("[%s] Configured %d datasets, %d algorithms, %d presenters.", self.name(), len(self.rawdata), len(self.algorithms), len(self.presenters))