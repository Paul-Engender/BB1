import typer
import datetime
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON, POST, BASIC

app = typer.Typer()

# --- CONFIGURATION ---
STORE_IP = "127.0.0.1"
QUERY_ENDPOINT = f"http://{STORE_IP}:3030/ds/query"
UPDATE_ENDPOINT = f"http://{STORE_IP}:3030/ds/update"
REVIEW_GRAPH = "http://my-org/ontology/review"
PERSIST_SKIPS = True

STATUS_PRED = "http://my-org/status"
REVIEWED_AT_PRED = "http://my-org/reviewedAt"

def get_sparql(endpoint, method=JSON):
    client = SPARQLWrapper(endpoint)
    client.setHTTPAuth(BASIC)
    client.setCredentials("admin", "admin")
    client.setReturnFormat(JSON)
    if method == POST:
        client.setMethod(POST)
    return client

def _escape_literal(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")

def write_decision(cls_uri: str, status: str, label: str):
    write_client = get_sparql(UPDATE_ENDPOINT, POST)
    timestamp = datetime.datetime.now().isoformat()
    label_safe = _escape_literal(label)
    
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    INSERT DATA {{
        GRAPH <{REVIEW_GRAPH}> {{
            <{cls_uri}> <{STATUS_PRED}> "{status}" .
            <{cls_uri}> <{REVIEWED_AT_PRED}> "{timestamp}" .
            <{cls_uri}> rdfs:label "{label_safe}" .
        }}
    }}
    """
    write_client.setQuery(query)
    write_client.query()

def get_next_class(read_client, skipped_uris: set):
    query_text = (Path(__file__).parent / "select_next.rq").read_text()
    excluded_str = ", ".join(f"<{u}>" for u in skipped_uris) or "<urn:noop>"
    query_text = query_text.replace("params_excluded_uris", excluded_str)
    
    read_client.setQuery(query_text)
    results = read_client.query().convert()
    bindings = results["results"]["bindings"]
    return bindings[0]["cls"]["value"] if bindings else None

def print_dossier(read_client, cls_uri):
    query_text = (Path(__file__).parent / "fetch_dossier.rq").read_text()
    query_text = query_text.replace("<params_cls_uri>", f"<{cls_uri}>")
    
    read_client.setQuery(query_text)
    results = read_client.query().convert()
    
    print("\n" + "="*90)
    print(f"📄 CLASS DOSSIER: {cls_uri}")
    print("="*90)
    
    current_section = ""
    label_found = "NO_LABEL"
    
    for row in results["results"]["bindings"]:
        section = row["section"]["value"]
        p = row["p"]["value"]
        o = row["o"]["value"]
        
        # Labels
        p_label = row.get("pLabel", {}).get("value", "")
        o_label = row.get("oLabel", {}).get("value", "")
        
        # SHACL stats
        min_c = row.get("min", {}).get("value", "")
        max_c = row.get("max", {}).get("value", "")
        
        # Capture class label for decision recorder
        if "prefLabel" in p or "label" in p:
            label_found = o

        # Section Header
        if section != current_section:
            print(f"\n🔹 {section}")
            current_section = section
        
        # --- Formatting Logic ---
        
        # 1. SHACL Properties: Show Property Name & Constraint Class
        if "SHACL:PROPS" in section:
            # Property Name <URI>
            prop_display = f"{p_label} <{p.split('#')[-1]}>" if p_label else p.split('#')[-1]
            # Constraint Class Name
            constraint_display = o_label if o_label else o.split('#')[-1]
            
            print(f"   • {prop_display}  ➔  Constraint: {constraint_display} | Min: {min_c} | Max: {max_c}")
            
        # 2. Incoming Links: Show "Property Name points here"
        elif "INCOMING" in section:
            prop_display = f"{p_label} <{p.split('#')[-1]}>" if p_label else p.split('#')[-1]
            print(f"   • Is Range of: {prop_display}")
            
        # 3. Standard Triples (Parents, Children, Logic)
        else:
            # Shorten Predicate URI for display
            p_short = p.split('#')[-1].split('/')[-1]
            # Show "Label <URI>" for Object
            o_display = f"{o_label} <{o}>" if (o_label and o_label != o) else o
            print(f"   • {p_short}: {o_display}")
            
    print("-" * 90)
    return label_found

@app.command()
def review():
    read_client = get_sparql(QUERY_ENDPOINT)
    skipped_uris = set()
    
    print("🚀 Starting Semantic Review (Top-Down Ordered)...")
    
    while True:
        try:
            cls_uri = get_next_class(read_client, skipped_uris)
            if not cls_uri:
                print("\n🎉 All caught up! No unreviewed classes (or parents) found.")
                break
            
            label = print_dossier(read_client, cls_uri)
            
            choice = input("\n👉 Action ([A]pprove / [R]eject / [S]kip / [Q]uit): ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 's':
                print("⏭️  Skipping...")
                skipped_uris.add(cls_uri)
                if PERSIST_SKIPS:
                    write_decision(cls_uri, "Skipped", label)
            elif choice == 'a':
                write_decision(cls_uri, "Approved", label)
                print("✅ Approved")
            elif choice == 'r':
                write_decision(cls_uri, "Rejected", label)
                print("❌ Rejected")
            else:
                print("⚠️ Invalid Input")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    app()