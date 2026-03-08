# Ontology Workspace (Temporary)

This directory contains temporary tools, scripts, and queries used to evolve and review the platform ontology while it is still maturing.

## Purpose
- Enable rapid iteration on ontology development.
- Support review workflows (e.g., SPARQL-based class review).
- Keep experimental tooling isolated from production kernel artifacts.

## Intended Migration
This workspace is **temporary by design**. Once the ontology and its governance process are mature, the contents of this directory are expected to move into a governed, long-lived repository or system.

## Contents
- `ontology_cli.py`: Review workflow CLI.
- `fetch_dossier.rq`: SPARQL query for class dossiers.
- `select_next.rq`: SPARQL query for selecting the next review target.
