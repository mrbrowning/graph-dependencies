from xml.etree import ElementTree


def get_dependencies(filename):
    return _get_dependencies_from_xml(_get_tree(filename))


def _get_tree(filename):
    return ElementTree.parse(filename).getroot()


def _get_dependencies_from_xml(tree):
    dependencies = {}

    for source_file in [f for f in tree.findall('file') if _is_project_file(f.attrib['path'])]:
        path = '/'.join(source_file.attrib['path'].split('/')[1:])
        dependents = [
            d.attrib['path'] for d in source_file.getchildren()
            if _is_project_file(d.attrib['path'])
        ]

        if dependents:
            dependencies[path] = [
                '/'.join(d.split('/')[1:]) for d in dependents
            ]

    return dependencies


def _is_project_file(filename):
    return filename.startswith('$PROJECT_DIR$') and filename.endswith('.java')
