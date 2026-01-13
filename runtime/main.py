import uuid
import os
from fastapi import FastAPI, HTTPException, Body, Response
from pydantic import BaseModel
from typing import Dict

from .kernel_gate import validate_abox

app = FastAPI(
    title="Kernel Gate Service",
    description="A thin API for validating and ingesting graphs against the Unified Operating Ontology.",
    version="0.1.0",
)

class ValidationResponse(BaseModel):
    conforms: bool
    report: str

@app.post("/validate", response_model=ValidationResponse)
async def validate_graph(
    graph_payload: str = Body(
        ..., 
        media_type="application/x-turtle",
        description="A graph in Turtle (text/turtle) format to validate against the kernel.",
        example="""
@prefix ex:     <https://ontology.engender.co.za/example#> .
@prefix kern:   <https://ontology.engender.co.za/kernel#> .

ex:Stipulation_456 a kern:Stipulation ;
    kern:hasStipulationNature kern:Restriction ;
    kern:stipulatesOn ex:TargetRef_123 ;
    kern:ruleExpression "size < 100" .
"""
    )
):
    """
    Validates a given ABox graph (in Turtle format) against the kernel SHACL shapes.
    """
    try:
        conforms, _, results_text = validate_abox(graph_payload)
        return ValidationResponse(conforms=conforms, report=results_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Turtle or validation error: {e}")

@app.post("/ingest")
async def ingest_graph(
    graph_payload: str = Body(
        ...,
        media_type="application/x-turtle",
        description="A graph in Turtle (text/turtle) format to ingest into the persistent store.",
    )
):
    """
    Validates and ingests a graph into the persistent store.
    """
    try:
        conforms, _, results_text = validate_abox(graph_payload)
        if not conforms:
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed. Graph does not conform to SHACL shapes:\n{results_text}"
            )

        graph_id = str(uuid.uuid4())
        file_path = os.path.join("data", f"{graph_id}.ttl")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(graph_payload)
        
        return {"message": f"Graph successfully ingested with ID: {graph_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Turtle or ingestion error: {e}")

@app.get("/graph/{graph_id}")
async def get_graph(graph_id: str):
    """
    Retrieves a named graph from the persistent store by its ID.
    """
    file_path = os.path.join("data", f"{graph_id}.ttl")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Graph with ID '{graph_id}' not found.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return Response(content=content, media_type="application/x-turtle")

@app.on_event("startup")
async def startup_event():
    # This will trigger the lru_cache to load the kernel graphs on startup
    from .kernel_gate import get_kernel_graphs
    print("Pre-loading kernel TBox and SHACL shapes...")
    get_kernel_graphs()
    print("Kernel graphs loaded.")

