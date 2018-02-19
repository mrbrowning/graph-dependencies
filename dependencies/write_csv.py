import csv
import logging
from collections import defaultdict


logging.basicConfig(level=logging.INFO)


def _is_class(dependency_entry):
    try:
        return dependency_entry[-1][0].isupper()
    except IndexError:
        logging.error('Got bad value: {}'.format(dependency_entry))


def _get_counter():
    i = 0
    def counter():
        nonlocal i
        result = i
        i += 1

        return result

    return counter


def _format_entity_name(entity):
    return '.'.join(entity)


def _get_records(trie):
    classes = defaultdict(_get_counter())
    packages = defaultdict(_get_counter())

    class_class_edges = set()
    class_package_edges = set()
    package_class_edges = set()
    package_package_edges = set()

    for depender, dependents in trie:
        if not depender:
            continue
        is_depender_class = _is_class(depender)
        depender_dict = classes if is_depender_class else packages

        for d in dependents:
            is_dependent_class = _is_class(d)

            dependent_dict = classes if is_dependent_class else packages
            edge = (depender_dict[depender], dependent_dict[d])

            if is_depender_class and is_dependent_class:
                class_class_edges.add(edge)
            elif is_depender_class and not is_dependent_class:
                class_package_edges.add(edge)
            elif not is_depender_class and is_dependent_class:
                package_class_edges.add(edge)
            else:
                package_package_edges.add(edge)

    return (
        classes,
        packages,
        class_class_edges,
        class_package_edges,
        package_class_edges,
        package_package_edges,
    )


def write_csv(
        trie,
        classes_file,
        packages_file,
        class_class_file,
        class_package_file,
        package_class_file,
        package_package_file):
    (
        classes,
        packages,
        class_class_edges,
        class_package_edges,
        package_class_edges,
        package_package_edges
    ) = _get_records(trie)

    for filename, entities in [(classes_file, classes), (packages_file, packages)]:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(('id', 'name'))

            for name, id in entities.items():
                writer.writerow((id, '.'.join(name)))
        
        logging.info('Wrote node file: {}'.format(filename))

    for edges_file, edges, columns in (
            (class_class_file, class_class_edges, ('class_id', 'class_id')),
            (class_package_file, class_package_edges, ('class_id', 'package_id')),
            (package_class_file, package_class_edges, ('package_id', 'class_id')),
            (package_package_file, package_package_edges, ('package_id', 'package_id'))):

        with open(edges_file, 'w', newline='') as f:
            writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(columns)

            for edge in edges:
                writer.writerow(edge)
        
        logging.info('Wrote edges file: {}'.format(edges_file))
