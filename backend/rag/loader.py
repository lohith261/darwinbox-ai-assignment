"""Policy document loading utilities."""

from pathlib import Path

from backend.rag.models import PolicySection


def load_policy_markdown(document_path: Path) -> list[PolicySection]:
    """Load a markdown policy file into titled sections."""
    text = document_path.read_text(encoding="utf-8").strip()
    sections: list[PolicySection] = []
    current_title = "Document Introduction"
    current_lines: list[str] = []
    order = 0

    def flush_section() -> None:
        """Construct PolicySection from buffered lines and clear buffer."""
        nonlocal order
        content = "\n".join(current_lines).strip()
        if not content:
            return
        sections.append(
            PolicySection(
                source=document_path,
                title=current_title,
                content=content,
                order=order,
            )
        )
        order += 1

    for line in text.splitlines():
        if line.startswith("## "):
            flush_section()
            current_title = line.removeprefix("## ").strip()
            current_lines = [line]
            continue
        current_lines.append(line)

    flush_section()
    return sections
