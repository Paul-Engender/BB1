import os
import uuid

from fastapi import Body, FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from .kernel_gate import validate_abox
from .runtime1_engine import Runtime1EngineError, build_support_ontology_release, evaluate_release_candidate

app = FastAPI(
    title="Kernel Gate Service",
    description=(
        "Runtime-1 support ontology service with kernel validation and "
        "evidence-bound release packaging."
    ),
    version="0.3.0",
)


class ValidationResponse(BaseModel):
    conforms: bool
    report: str


class ReleaseCandidateResponse(BaseModel):
    engine: str
    generated_at: str
    accepted: bool
    summary: dict
    checks: list[dict]


class BuildSupportReleaseRequest(BaseModel):
    release_version: str = Field(default="0.2.0")
    output_root: str = Field(default="dist")
    deterministic: bool = Field(default=True)
    run_promotion_gate: bool = Field(default=True)


class BuildSupportReleaseResponse(BaseModel):
    release_id: str
    manifest_path: str
    archive_path: str
    evidence_files: list[str]
    promotion_decision_path: str
    loader_verification_message: str
    accepted: bool


@app.post("/validate", response_model=ValidationResponse)
async def validate_graph(
    graph_payload: str = Body(
        ...,
        media_type="application/x-turtle",
        description="A graph in Turtle format to validate against the kernel.",
    )
):
    """Validate ABox graph (Turtle) against kernel SHACL shapes."""
    try:
        conforms, _, results_text = validate_abox(graph_payload)
        return ValidationResponse(conforms=conforms, report=results_text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Turtle or validation error: {exc}")


@app.post("/runtime1/release-candidate/evaluate", response_model=ReleaseCandidateResponse)
async def evaluate_runtime1_release_candidate():
    """Evaluate Runtime-1 release candidate and return structured evidence results."""
    try:
        return ReleaseCandidateResponse(**evaluate_release_candidate())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Release-candidate evaluation failed: {exc}")


@app.post("/runtime1/support-release/build", response_model=BuildSupportReleaseResponse)
async def build_runtime1_support_release(request: BuildSupportReleaseRequest):
    """Build evidence-bound SupportOntologyRelease package from current ontology payload."""
    try:
        result = build_support_ontology_release(
            release_version=request.release_version,
            output_root=request.output_root,
            deterministic=request.deterministic,
            run_promotion_gate=request.run_promotion_gate,
        )
        return BuildSupportReleaseResponse(
            release_id=result["release_id"],
            manifest_path=result["manifest_path"],
            archive_path=result["archive_path"],
            evidence_files=result["evidence_files"],
            promotion_decision_path=result["promotion_decision_path"],
            loader_verification_message=result["loader_verification_message"],
            accepted=bool(result["evaluation"]["accepted"]),
        )
    except Runtime1EngineError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Support-release build failed: {exc}")


@app.post("/ingest")
async def ingest_graph(
    graph_payload: str = Body(
        ...,
        media_type="application/x-turtle",
        description="A graph in Turtle format to ingest into the persistent store.",
    )
):
    """Validate and ingest a graph into local persistent storage."""
    try:
        conforms, _, results_text = validate_abox(graph_payload)
        if not conforms:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Validation failed. Graph does not conform to SHACL shapes:\n"
                    f"{results_text}"
                ),
            )

        graph_id = str(uuid.uuid4())
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", f"{graph_id}.ttl")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(graph_payload)

        return {"message": f"Graph successfully ingested with ID: {graph_id}"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Turtle or ingestion error: {exc}")


@app.get("/graph/{graph_id}")
async def get_graph(graph_id: str):
    """Retrieve a named graph from local storage by its ID."""
    file_path = os.path.join("data", f"{graph_id}.ttl")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Graph with ID '{graph_id}' not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return Response(content=content, media_type="application/x-turtle")


@app.on_event("startup")
async def startup_event():
    from .kernel_gate import get_kernel_graphs

    print("Pre-loading kernel TBox and SHACL shapes...")
    get_kernel_graphs()
    print("Kernel graphs loaded.")
