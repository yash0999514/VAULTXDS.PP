"""Hierarchical Category Tree structure for organizing document classifications.

Academic Specifications:
- Time Complexity:
  - Add Child: O(B) where B is the branching factor.
  - Search (find): O(N) where N is the total node count.
  - Path Resolution: O(D) where D is depth of tree.
- Space Complexity: O(N) nodes.
"""

from typing import Any, Dict, List, Optional


class CategoryTreeNode:
    """A node representing a document category with parent/child relationships."""

    def __init__(
        self,
        name: str,
        category_id: Optional[int] = None,
        parent: Optional["CategoryTreeNode"] = None,
    ):
        self.name = name.strip()
        self.category_id = category_id
        self.parent = parent
        self.children: List["CategoryTreeNode"] = []
        self.document_count: int = 0

    def add_child(self, name: str, category_id: Optional[int] = None) -> "CategoryTreeNode":
        """Add child node if not existing, or return existing matching child."""
        clean_name = name.strip()
        for child in self.children:
            if child.name.lower() == clean_name.lower():
                if category_id is not None:
                    child.category_id = category_id
                return child

        child = CategoryTreeNode(clean_name, category_id=category_id, parent=self)
        self.children.append(child)
        return child

    def find(self, name: str) -> Optional["CategoryTreeNode"]:
        """Locate category node by case-insensitive name."""
        if self.name.lower() == name.strip().lower():
            return self
        for child in self.children:
            found = child.find(name)
            if found:
                return found
        return None

    def find_by_id(self, category_id: int) -> Optional["CategoryTreeNode"]:
        """Locate category node by database primary key ID."""
        if self.category_id == category_id:
            return self
        for child in self.children:
            found = child.find_by_id(category_id)
            if found:
                return found
        return None

    def get_full_path(self) -> str:
        """Return slash-delimited breadcrumb path from root down to this category."""
        if self.parent is None or self.parent.name == "Root":
            return self.name
        return f"{self.parent.get_full_path()}/{self.name}"

    def list_all_paths(self) -> List[str]:
        """Return list of all full paths in this tree subtree."""
        paths = []
        if self.name != "Root":
            paths.append(self.get_full_path())
        for child in self.children:
            paths.extend(child.list_all_paths())
        return paths

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tree into nested dictionary format."""
        return {
            "name": self.name,
            "category_id": self.category_id,
            "document_count": self.document_count,
            "children": [c.to_dict() for c in self.children],
        }

    def render_ascii_tree(self, prefix: str = "", is_last: bool = True) -> str:
        """Render beautiful ASCII visual tree representation for academic viva display."""
        connector = "└── " if is_last else "├── "
        count_str = f" ({self.document_count} docs)" if self.document_count > 0 else ""
        lines = [f"{prefix}{connector}{self.name}{count_str}"] if self.name != "Root" else ["📁 Categories Root"]

        new_prefix = prefix + ("    " if is_last else "│   ") if self.name != "Root" else ""
        count = len(self.children)
        for i, child in enumerate(self.children):
            lines.append(child.render_ascii_tree(new_prefix, i == count - 1))
        return "\n".join(lines)


def build_category_tree(records: List[Dict[str, Any]]) -> CategoryTreeNode:
    """Reconstruct an in-memory CategoryTree from database rows."""
    root = CategoryTreeNode("Root", category_id=None)
    nodes_by_id: Dict[int, CategoryTreeNode] = {}

    # Pass 1: create nodes
    for rec in records:
        cat_id = rec["id"]
        node = CategoryTreeNode(name=rec["name"], category_id=cat_id)
        nodes_by_id[cat_id] = node

    # Pass 2: link parents and children
    for rec in records:
        cat_id = rec["id"]
        parent_id = rec.get("parent_id")
        node = nodes_by_id[cat_id]
        if parent_id and parent_id in nodes_by_id:
            parent_node = nodes_by_id[parent_id]
            node.parent = parent_node
            parent_node.children.append(node)
        else:
            node.parent = root
            root.children.append(node)

    return root
