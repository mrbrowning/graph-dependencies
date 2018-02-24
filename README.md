Overview
========

This project takes an XML file from IntelliJ describing a project's package- and class-level dependencies and ingests it into Neo4j as a graph that contains directed edges for both dependencies (with the depender having an outgoing edge to the dependee) and sub-packages/-classes (with the container having an outgoing edge to the containee). It assumes that Neo4j is running locally in its default configuration, listening on `localhost:7687`, with admin username `neo4j` and admin password `neo4j`. To change username or password, modify the relevant environment variables in the `Makefile`.

Getting Started
---------------

To execute the complete process of ingesting your dependencies into Neo4j, just run:

    make all

Since the community edition of Neo4j only supports a single local database instance, you'll need to drop all existing nodes and edges if you want to load a different project's dependencies for analysis. In this case, you can run:

    make drop

To clear the local instance of all its entities.
