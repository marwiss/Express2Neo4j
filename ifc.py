from neo4j import GraphDatabase
import re
import argparse


def visualize(file, graph_uri):
    ifc_file = ''.join(open(file, "r").readlines())
    driver = GraphDatabase.driver(graph_uri)
    driver.verify_connectivity()

    with driver.session() as session:
        for entity in re.finditer(r'ENTITY (\w+).+?SUBTYPE OF \((\w+?)\).+?END_ENTITY', ifc_file, re.DOTALL):
            cypher = """
                 MERGE (e1:Entity {name: $e1})
                    SET e1.express = $e
                 MERGE (e2:Entity {name: $e2})
                 MERGE (e1)-[r:IS_SUBTYPE_OF]-(e2)
                 RETURN e1.name as e1, TYPE(r) as r, e2.name as e2
            """
            result = session.run(cypher, e1=entity.group(1), e=entity.group(), e2=entity.group(2))
            first = result.single()
            print(first.get('e1'), first.get('r'), first.get('e2'))


if __name__ == "__main__":
    USAGE = "Visualize IFC EXPRESS schema.\nUsage: python ifc.py -f /path/filename -g URI"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument('-f', '--file', type=str, help='Input IFC EXPRESS path and file name', default='IFC.exp')
    parser.add_argument('-g', '--graph', type=str, help='Connect URI for Neo4j server',
                        default='bolt://localhost:7687')
    args = parser.parse_args()
    visualize(args.file, args.graph)
