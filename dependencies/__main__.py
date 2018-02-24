import sys

import dependencies.read_xml as read_xml
import dependencies.trie as trie
import dependencies.write_csv as write_csv


def main(argv):
    (
        dependencies_file,
        classes_file,
        packages_file,
        class_class_file,
        class_package_file,
        package_class_file,
        package_package_file,
        class_child_file,
        package_child_file,
    ) = argv

    dependencies = read_xml.get_dependencies(dependencies_file)
    dependency_trie = trie.from_file_dependencies(dependencies)

    write_csv.write_csv(
        dependency_trie,
        classes_file,
        packages_file,
        class_class_file,
        class_package_file,
        package_class_file,
        package_package_file,
        class_child_file,
        package_child_file,
    )


if __name__ == '__main__':
    main(sys.argv[1:])
