#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Copyright (C) 2018-2019  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
#

from pathlib import Path

import json

from pydsdl import read_namespace
from nunavut import build_namespace_tree, Namespace
from nunavut.lang import LanguageContext
from nunavut.jinja import DSDLCodeGenerator
from nunavut.jinja.loaders import TEMPLATE_SUFFIX


class a:
    pass


class b(a):
    pass


class c(a):
    pass


class d(b, c):
    pass


def test_bfs_of_type_for_template(gen_paths):  # type: ignore
    """ Verifies that our template to type lookup logic does a breadth-first search for a valid
    template when searching type names.
    """
    language_context = LanguageContext(extension='.json')
    empty_namespace = Namespace('',
                                gen_paths.dsdl_dir,
                                gen_paths.out_dir,
                                language_context)
    generator = DSDLCodeGenerator(empty_namespace, templates_dir=gen_paths.templates_dir)
    subject = d()
    template_file = generator.filter_type_to_template(subject)
    assert str(Path('c').with_suffix(TEMPLATE_SUFFIX)) == template_file
    assert generator.filter_type_to_template(subject) == template_file


def test_one_template(gen_paths):  # type: ignore
    """ Verifies that we can use only a SeralizableType.j2 as the only template when
    no service types are present.
    """
    root_namespace_dir = gen_paths.dsdl_dir / Path("uavcan")
    root_namespace = str(root_namespace_dir)
    serializable_types = read_namespace(root_namespace, [])
    language_context = LanguageContext(extension='.json')
    namespace = build_namespace_tree(serializable_types,
                                     root_namespace_dir,
                                     gen_paths.out_dir,
                                     language_context)
    generator = DSDLCodeGenerator(namespace, templates_dir=gen_paths.templates_dir)
    generator.generate_all(False)

    outfile = gen_paths.find_outfile_in_namespace("uavcan.time.TimeSystem", namespace)
    assert (outfile is not None)

    with open(str(outfile), 'r') as json_file:
        json_blob = json.load(json_file)

    assert json_blob['uavcan.time.TimeSystem']['namespace'] == 'uavcan.time'
    assert json_blob['uavcan.time.TimeSystem']['is_serializable']


def test_get_templates(gen_paths):  # type: ignore
    """
    Verifies the nunavut.jinja.DSDLCodeGenerator.get_templates() method.
    """
    root_namespace_dir = gen_paths.dsdl_dir / Path("uavcan")
    root_namespace = str(root_namespace_dir)
    serializable_types = read_namespace(root_namespace, [])
    language_context = LanguageContext(extension='.json')
    namespace = build_namespace_tree(serializable_types,
                                     root_namespace_dir,
                                     gen_paths.out_dir,
                                     language_context)
    generator = DSDLCodeGenerator(namespace, templates_dir=gen_paths.templates_dir)

    templates = generator.get_templates()

    count = 0
    for template in templates:
        count += 1
    assert count > 0

    # Do it twice just to cover in-memory cache
    templates = generator.get_templates()

    count = 0
    for template in templates:
        count += 1
    assert count > 0
