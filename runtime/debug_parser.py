import rdflib
from pathlib import Path

def main():
    tbox_path = Path("/home/user/AA1/ontology/kernel.ttl")
    g = rdflib.Graph()
    try:
        g.parse(str(tbox_path), format="turtle")
        print(f"Successfully parsed {tbox_path}")
        print(f"Graph contains {len(g)} triples.")

        q = "select ?s ?p ?o where { ?s ?p ?o }"
        for r in g.query(q):
            print(r)

    except Exception as e:
        print(f"Failed to parse {tbox_path}: {e}")

if __name__ == "__main__":
    main()
