from __future__ import annotations

from collections import Counter

from data_eval_factory.benchmark.rubrics import rubric_for
from data_eval_factory.benchmark.taxonomy import TAXONOMY
from data_eval_factory.schemas.benchmark import BenchmarkItem, BenchmarkManifest
from data_eval_factory.schemas.ticket import Ticket


def build_benchmark(
    tickets: list[Ticket],
    version: str,
    dataset_sha256: str,
    notes: list[str],
) -> tuple[list[BenchmarkItem], BenchmarkManifest]:
    selected = [ticket for ticket in tickets if ticket.split == "test"]
    items = [
        BenchmarkItem(
            id=f"{version}-{ticket.id}",
            version=version,
            ticket_id=ticket.id,
            tasks=ticket.tasks,
            difficulty=ticket.difficulty,
            slices=ticket.slices,
            rubric_id=rubric_for(ticket.tasks),
            gold_type=ticket.gold_type,
            gold_tool=ticket.gold_tool,
            relevant_doc_ids=ticket.relevant_doc_ids,
        )
        for ticket in selected
    ]
    task_counts = Counter(task for item in items for task in item.tasks)
    for family in TAXONOMY:
        task_counts.setdefault(family, 0)
    manifest = BenchmarkManifest(
        version=version,
        item_count=len(items),
        task_counts=dict(sorted(task_counts.items())),
        difficulty_counts=dict(sorted(Counter(item.difficulty for item in items).items())),
        slice_counts=dict(sorted(Counter(name for item in items for name in item.slices).items())),
        dataset_sha256=dataset_sha256,
        notes=notes,
    )
    return items, manifest
