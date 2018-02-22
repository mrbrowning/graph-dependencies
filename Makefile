NEO4J_IMPORT_DIR="/usr/local/Cellar/neo4j/3.3.0/libexec/import"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="neo4j"

.PHONY: all clean drop move ingest ingest_classes ingest_packages ingest_class_class ingest_class_package ingest_package_class ingest_package_package

all: ingest

clean:
	rm *.csv
	rm ${NEO4J_IMPORT_DIR}/*.csv

drop:
	echo "MATCH (n) DETACH DELETE n;" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}

classes.csv packages.csv class_class.csv class_package.csv package_class.csv package_package.csv : data/dependencies.xml
	# Make has no concept of a single rule always writing to all of its targets, so have to be explicit here.
	python3 -m dependencies $< classes.csv packages.csv class_class.csv class_package.csv package_class.csv package_package.csv

move: classes.csv packages.csv class_class.csv class_package.csv package_class.csv package_package.csv
	for f in $^ ; do cp $$f ${NEO4J_IMPORT_DIR}/ ; done

ingest_classes: classes.csv
	echo "LOAD CSV WITH HEADERS FROM \"file:///$<\" AS csvLine CREATE (c:Class { id: toInteger(csvLine.id), name: csvLine.name });" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}
	echo "CREATE CONSTRAINT ON (c:Class) ASSERT c.id IS UNIQUE;"

ingest_packages: packages.csv
	echo "LOAD CSV WITH HEADERS FROM \"file:///$<\" AS csvLine CREATE (p:Package { id: toInteger(csvLine.id), name: csvLine.name });" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}
	echo "CREATE CONSTRAINT ON (p:Package) ASSERT p.id IS UNIQUE;"

ingest_class_class: class_class.csv
	echo "USING PERIODIC COMMIT 500 LOAD CSV WITH HEADERS FROM \"file:///$<\" AS csvLine MATCH (c1:Class { id: toInteger(csvLine.class1_id)}), (c2:Class { id: toInteger(csvLine.class2_id)}) CREATE (c1)-[:DEPENDS_ON]->(c2);" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}

ingest_class_package: class_package.csv
	echo "USING PERIODIC COMMIT 500 LOAD CSV WITH HEADERS FROM \"file:///$<\" AS csvLine MATCH (c:Class { id: toInteger(csvLine.class_id)}), (p:Package { id: toInteger(csvLine.package_id)}) CREATE (c)-[:DEPENDS_ON]->(p);" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}

ingest_package_class: package_class.csv
	echo "USING PERIODIC COMMIT 500 LOAD CSV WITH HEADERS FROM \"file:///$<\" AS csvLine MATCH (p:Package { id: toInteger(csvLine.package_id)}), (c:Class { id: toInteger(csvLine.class_id)}) CREATE (p)-[:DEPENDS_ON]->(c);" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}

ingest_package_package: package_package.csv
	echo "USING PERIODIC COMMIT 500 LOAD CSV WITH HEADERS FROM \"file:///$<\" AS csvLine MATCH (p1:Package { id: toInteger(csvLine.package1_id)}), (p2:Package { id: toInteger(csvLine.package2_id)}) CREATE (p1)-[:DEPENDS_ON]->(p2);" | cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD}

ingest: move ingest_classes ingest_packages ingest_class_class ingest_class_package ingest_package_class ingest_package_package
