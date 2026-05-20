"""Performance analysis module"""

import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)


class PerformanceIssue:
    """Represents a performance issue"""

    def __init__(self, severity: str, issue_type: str, message: str, suggestion: str = ""):
        self.severity = severity  # HIGH, MEDIUM, LOW
        self.type = issue_type
        self.message = message
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "type": self.type,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class PerformanceAnalyzer:
    """Analyzes queries for performance issues"""

    def analyze(self, query: str) -> List[PerformanceIssue]:
        """Analyze query for performance issues"""
        issues = []

        issues.extend(self._check_select_all(query))
        issues.extend(self._check_missing_indexes(query))
        issues.extend(self._check_subqueries(query))
        issues.extend(self._check_joins(query))
        issues.extend(self._check_group_by(query))

        return issues

    def _check_select_all(self, query: str) -> List[PerformanceIssue]:
        """Check for SELECT * usage"""
        issues = []

        if re.search(r"SELECT\s+\*", query, re.IGNORECASE):
            issues.append(
                PerformanceIssue(
                    severity="MEDIUM",
                    issue_type="SELECT_ALL",
                    message="SELECT * fetches all columns",
                    suggestion="Specify only required columns",
                )
            )

        return issues

    def _check_missing_indexes(self, query: str) -> List[PerformanceIssue]:
        """Check for queries that might benefit from indexes"""
        issues = []

        # Check for unindexed WHERE conditions
        if re.search(r"WHERE\s+.+\s+(OR|AND)", query, re.IGNORECASE):
            issues.append(
                PerformanceIssue(
                    severity="MEDIUM",
                    issue_type="INDEX",
                    message="Complex WHERE clause might need index",
                    suggestion="Consider adding indexes on frequently queried columns",
                )
            )

        return issues

    def _check_subqueries(self, query: str) -> List[PerformanceIssue]:
        """Check for inefficient subqueries"""
        issues = []

        subquery_count = query.count("SELECT") - 1
        if subquery_count > 2:
            issues.append(
                PerformanceIssue(
                    severity="MEDIUM",
                    issue_type="SUBQUERY",
                    message=f"Query contains {subquery_count} subqueries",
                    suggestion="Consider using JOINs instead of subqueries",
                )
            )

        return issues

    def _check_joins(self, query: str) -> List[PerformanceIssue]:
        """Check for join optimization"""
        issues = []

        join_count = len(re.findall(r"JOIN", query, re.IGNORECASE))
        if join_count > 3:
            issues.append(
                PerformanceIssue(
                    severity="LOW",
                    issue_type="JOIN",
                    message=f"Query contains {join_count} joins",
                    suggestion="Consider query complexity and consider denormalization if needed",
                )
            )

        return issues

    def _check_group_by(self, query: str) -> List[PerformanceIssue]:
        """Check GROUP BY optimization"""
        issues = []

        if "GROUP BY" in query.upper() and "ORDER BY" in query.upper():
            if query.upper().index("GROUP BY") > query.upper().index("ORDER BY"):
                issues.append(
                    PerformanceIssue(
                        severity="LOW",
                        issue_type="GROUP_BY",
                        message="ORDER BY after GROUP BY might need optimization",
                        suggestion="Ensure proper index on GROUP BY columns",
                    )
                )

        return issues
