"""
This module contains IO utility functions for amateur rocketry file formats.
"""
import xml.etree.ElementTree as ET
import collections
import pandas

class RSEParseError(RuntimeError):
    """
    Raised when there is an error parsing a RockSim file.
    """

_Engine = collections.namedtuple("Engine", ["code", "manufacturer",
                                            "comments", "data"])

class Engine(_Engine):
    """
    An individual engine record.

    The thrust curve data is represented by a pandas DataFrame object, with the
    following columns: time (seconds), force (Newtons), mass (grams).

    Attributes:
        manufacturer: A string containing the manufacturer, or None
        code: A string containing the maufacturer's product code, or None
        comments: A string containing any comments, or None
        data: A pandas DataFrame, see above
    """
    # See: http://stackoverflow.com/questions/1606436
    __slots__ = ()

def _get_float_attr(elem, attr, default=None):
    v = elem.get(attr)
    if v is None:
        return default
    return float(v)

def _parse_engine(engine):
    comments_elem = engine.find("comments")
    comments = comments_elem.text if comments_elem is not None else None

    data_elem = _find_or_raise(engine, 'data')
    data_records = []
    for datum in data_elem.iterfind("eng-data"):
        data_records.append((
            _get_float_attr(datum, "t"),
            _get_float_attr(datum, "f"),
            _get_float_attr(datum, "m"),
        ))
    data = pandas.DataFrame.from_records(data_records,
                                         columns=['time', 'force', 'mass'])

    return Engine(code=engine.get("code"), manufacturer=engine.get("mfg"),
                  comments=comments, data=data)

def _find_or_raise(elem, tag):
    child = elem.find(tag)
    if child is None:
        raise RSEParseError("Could not find expected element: %s" % tag)
    return child

def rse_load(path):
    """
    Load a RockSim format engine database from disk.

    Args:
        path (str): path name to .rse file

    Returns:
        A list of Engine instances.

    Raises:
        RSEParseError: when the .rse file is invalid
    """
    tree = ET.parse(path)
    root = tree.getroot()

    if root.tag != "engine-database":
        raise RSEParseError("Expected engine-database tag.")

    engine_list = _find_or_raise(root, 'engine-list')

    return [_parse_engine(e) for e in engine_list.iterfind("engine")]
