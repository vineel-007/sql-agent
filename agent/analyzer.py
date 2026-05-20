"""Main SQL Analyzer"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from agent.modules import (
    SQLValidator,
    ValidationResult,
    SecurityAnalyzer,
    PerformanceAnalyzer,
    ExplanationGenerator,
)
from agent.db_connector import DatabaseConnector
from agent.config import Config

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Analysis result"""

    valid: bool
    validation_errors: List[Dict[str, Any]]
    security_issues: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    explanation: str
    optimized_query: str
    exact_query: str


class SQLAnalyzer:
    """Main SQL Query Analyzer"""

    def __init__(self, llm_provider: str = "openai", db_connection: Optional[DatabaseConnector] = None):
        self.llm_provider = llm_provider
        self.db_connection = db_connection
        self.validator = SQLValidator()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.explanation_generator = ExplanationGenerator()
        self._init_llm()

    def _init_llm(self):
        """Initialize LLM client"""
        try:
            if self.llm_provider == "openai":
                from agent.llm import OpenAIClient

                self.llm = OpenAIClient(
                    api_key=Config.OPENAI_API_KEY,
                    model=Config.LLM_MODEL,
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS,
                )
            elif self.llm_provider == "claude":
                from agent.llm import ClaudeClient

                self.llm = ClaudeClient(
                    api_key=Config.CLAUDE_API_KEY,
                    model=Config.LLM_MODEL,
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS,
                )
            else:
                logger.warning(f"Unknown LLM provider: {self.llm_provider}")
                self.llm = None
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            self.llm = None

    def analyze(self, query: str, execute: bool = False) -> AnalysisResult:
        """Analyze SQL query"""
        # Validate
        validation_result = self.validator.validate(query)

        # Security analysis
        security_issues = self.security_analyzer.analyze(query)

        # Performance analysis
        performance_issues = self.performance_analyzer.analyze(query)

        # Explanation
        explanation = self.explanation_generator.explain(query)

        # Get optimized query from LLM
        optimized_query = self._get_optimized_query(query) if self.llm else query

        # Get exact query
        exact_query = self._get_exact_query(query)

        return AnalysisResult(
            valid=validation_result.valid,
            validation_errors=[e.to_dict() for e in validation_result.errors],
            security_issues=[s.to_dict() for s in security_issues],
            performance_issues=[p.to_dict() for p in performance_issues],
            explanation=explanation,
            optimized_query=optimized_query,
            exact_query=exact_query,
        )

    def _get_optimized_query(self, query: str) -> str:
        """Get optimized query from LLM"""
        if not self.llm:
            return query

        prompt = f"""Optimize this SQL query for better performance:

{query}

Provide ONLY the optimized SQL query, no explanation."""

        return self.llm.query(prompt)

    def _get_exact_query(self, query: str) -> str:
        """Get exact formatted query"""
        import sqlparse

        return sqlparse.format(
            query,
            reindent=True,
            keyword_case="upper",
            use_space_around_operators=True,
        )

    def analyze_comprehensive(self, query: str) -> AnalysisResult:
        """Run comprehensive analysis"""
        return self.analyze(query, execute=False)
