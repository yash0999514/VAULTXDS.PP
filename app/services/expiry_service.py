"""Expiry tracking service using reliable chronological date sorting."""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ExpiryService:
    """Manages document expiration tracking using accurate chronological date sorting."""

    def __init__(self):
        # Maps doc_id -> entry dictionary
        self._records: Dict[int, Dict[str, Any]] = {}

    def add_expiry(self, doc_id: int, expiry_date_str: str, metadata: Any = None) -> bool:
        """Parse expiry date string and record document deadline."""
        if not expiry_date_str or not expiry_date_str.strip():
            return False
        try:
            dt = datetime.strptime(expiry_date_str.strip(), "%Y-%m-%d")
            self._records[doc_id] = {
                "doc_id": doc_id,
                "timestamp": dt.timestamp(),
                "expiry_date": dt.strftime("%Y-%m-%d"),
                "metadata": metadata or {},
            }
            return True
        except ValueError:
            return False

    def update_expiry(self, doc_id: int, expiry_date_str: Optional[str], metadata: Any = None) -> None:
        """Update or remove document expiration tracking."""
        if doc_id in self._records:
            del self._records[doc_id]
        if expiry_date_str:
            self.add_expiry(doc_id, expiry_date_str, metadata)

    def remove_expiry(self, doc_id: int) -> bool:
        """Remove document from expiration tracker upon deletion."""
        if doc_id in self._records:
            del self._records[doc_id]
            return True
        return False

    def get_expiring_within_days(self, days: int = 30) -> List[Dict[str, Any]]:
        """Retrieve documents expiring within the specified number of days, ordered by nearest deadline."""
        now = datetime.now()
        cutoff_ts = now.timestamp() + (days * 86400)
        results = []
        for doc_id, rec in self._records.items():
            if rec["timestamp"] <= cutoff_ts:
                exp_date = datetime.fromtimestamp(rec["timestamp"])
                days_left = (exp_date.date() - now.date()).days
                results.append({
                    "doc_id": doc_id,
                    "expiry_date": rec["expiry_date"],
                    "days_left": days_left,
                    "is_expired": days_left < 0,
                    "metadata": rec["metadata"],
                })
        results.sort(key=lambda x: x["days_left"])
        return results

    def get_all_tracked(self) -> List[Dict[str, Any]]:
        """Return all tracked documents sorted chronologically by nearest expiration date."""
        now = datetime.now()
        results = []
        for doc_id, rec in self._records.items():
            exp_date = datetime.fromtimestamp(rec["timestamp"])
            days_left = (exp_date.date() - now.date()).days
            results.append({
                "doc_id": doc_id,
                "expiry_date": rec["expiry_date"],
                "days_left": days_left,
                "is_expired": days_left < 0,
                "metadata": rec["metadata"],
            })
        results.sort(key=lambda x: x["days_left"])
        return results

    def clear(self) -> None:
        """Clear all tracked records."""
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)
