"""
Results analysis and feedback generation for the LLM Quiz Challenge.

This module provides analysis of quiz results and generates comprehensive
feedback for students and instructors.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .quiz_runner import QuizResults, QuestionResult
from .validator import ValidationIssue

logger = logging.getLogger(__name__)


@dataclass
class FeedbackSection:
    """Represents a section of feedback with title and content."""
    title: str
    content: List[str]
    emoji: str = "📝"


class ResultsAnalyzer:
    """Analyzes quiz results and generates comprehensive feedback."""

    def __init__(self):
        """Initialize the results analyzer."""
        pass

    def generate_student_feedback(self, results: QuizResults) -> str:
        """Generate comprehensive feedback for students.

        Args:
            results: Quiz results to analyze

        Returns:
            Formatted feedback string
        """
        sections = []

        # GitHub Classroom marker
        marker = "STUDENTS_QUIZ_KEIKO_WIN" if results.student_passes else "STUDENTS_QUIZ_KEIKO_LOSE"

        # Header section
        header = self._create_header_section(results, marker)
        sections.append(header)

        # Detailed question analysis
        question_analysis = self._create_question_analysis_section(results)
        sections.append(question_analysis)

        # Validation feedback (if there are issues)
        if results.invalid_questions > 0:
            validation_feedback = self._create_validation_feedback_section(results)
            sections.append(validation_feedback)

        # Performance feedback
        performance_feedback = self._create_performance_feedback_section(results)
        sections.append(performance_feedback)

        # Remove general tips section as requested

        return self._format_feedback_sections(sections, marker)

    def generate_instructor_summary(self, results: QuizResults) -> Dict[str, Any]:
        """Generate summary for instructors.

        Args:
            results: Quiz results to analyze

        Returns:
            Dictionary with instructor-focused analysis
        """
        return {
            "overall_performance": self._analyze_overall_performance(results),
            "validation_analysis": self._analyze_validation_patterns(results),
            "question_difficulty": self._analyze_question_difficulty(results),
            "common_issues": self._identify_common_issues(results),
            "recommendations": self._generate_instructor_recommendations(results)
        }

    def get_detailed_statistics(self, results: QuizResults) -> Dict[str, Any]:
        """Generate detailed statistics about the quiz performance.

        Args:
            results: Quiz results to analyze

        Returns:
            Detailed statistics dictionary
        """
        valid_results = [qr for qr in results.question_results
                        if qr.question.validation_result and qr.question.validation_result.valid]

        stats = {
            "quiz_overview": {
                "total_questions": results.total_questions,
                "valid_questions": results.valid_questions,
                "invalid_questions": results.invalid_questions,
                "system_errors": results.system_errors,
                "validation_rate": results.valid_questions / results.total_questions if results.total_questions > 0 else 0
            },
            "performance_metrics": {
                "student_wins": results.student_wins,
                "llm_wins": results.llm_wins,
                "success_rate": results.student_success_rate,
                "passes_challenge": results.student_passes
            },
            "question_analysis": {
                "avg_answer_length": self._calculate_avg_answer_length(valid_results),
                "confidence_distribution": self._analyze_confidence_distribution(valid_results),
                "error_types": self._categorize_errors(results.question_results)
            },
            "validation_breakdown": self._analyze_validation_breakdown(results)
        }

        return stats

    def _create_header_section(self, results: QuizResults, marker: str) -> FeedbackSection:
        """Create the header section with overall results."""
        content = [
            "="*80,
            "LLM QUIZ CHALLENGE RESULTS",
            "="*80,
            " ",
            f"Quiz: {results.quiz_title}",
            " ",
            f"Quiz Model: {results.quiz_model}",
            " ",
            f"Evaluator Model: {results.evaluator_model}",
            " ",
            f"Total Questions: {results.total_questions}",
            " ",
            f"Valid Questions: {results.valid_questions}",
            " ",
        ]

        if results.invalid_questions > 0:
            content.append(f"Invalid Questions: {results.invalid_questions} ❌")
        if results.system_errors > 0:
            content.append(f"System Errors: {results.system_errors} ⚠️")

        content.extend([
            "",
            f"Student Wins: {results.student_wins}",
            " ",
            f"LLM Wins: {results.llm_wins}",
            " ",
            f"Student Success Rate: {results.student_success_rate:.1%}"
            " ",
        ])

        # Add pass/fail indicator
        if results.student_passes:
            content.append("🎉 RESULT: PASS - You successfully challenged the LLM!")
        else:
            if results.valid_questions == 0:
                content.append("❌ RESULT: FAIL - No valid questions submitted")
            else:
                content.append("❌ RESULT: FAIL - Need to win 100% of valid questions (stump the LLM on ALL questions)")

        return FeedbackSection("Overall Results", content, "📊")

    def _create_question_analysis_section(self, results: QuizResults) -> FeedbackSection:
        """Create detailed analysis of each question."""
        content = [
            "="*80,
            "DETAILED QUESTION ANALYSIS",
            "="*80
        ]

        for qr in results.question_results:
            if qr.question.validation_result and not qr.question.validation_result.valid:
                content.extend([
                    f"\n❌ Question {qr.question.number}: INVALID",
                    "─"*60,
                    f"Question: {qr.question.question}",
                    " ",
                    f"🚫 Validation Issues:",
                    f"   {qr.question.validation_result.reason}",
                    " ",
                    "❌ Question: Invalid",
                    ""
                ])
                if qr.question.validation_result.issues:
                    for issue in qr.question.validation_result.issues:
                        content.append(f"   • {issue.value.replace('_', ' ').title()}")
                continue

            if qr.error:
                content.extend([
                    f"\n⚠️  Question {qr.question.number}: SYSTEM ERROR",
                    "─"*60,
                    f"Question: {qr.question.question}",
                    " ",
                    f"🔧 System Issues:",
                    f"   {qr.evaluation_explanation}",
                    " ",
                    f"⚠️  Result: This question was not counted due to system errors.",
                    ""
                ])
                continue

            winner_emoji = "🎉" if qr.student_wins else "🤖"
            winner = "Student" if qr.student_wins else "LLM"

            content.extend([
                " ",
                " ",
                f"\n📝 Question {qr.question.number}: {winner_emoji} {winner} wins",
                "─"*60,
                f"Question: {qr.question.question}",
                " ",
                f"💡 Your Expected Answer:",
                f"{qr.question.answer}",
                " ",
                f"🤖 LLM's Answer:",
                f"{qr.llm_answer}",
                " ",
                f"⚖️  Evaluator's Verdict: {'CORRECT' if qr.is_correct else 'INCORRECT'}",
                " ",
                f"📝 Evaluation: {qr.evaluation_explanation}",
                " "
            ])

            # Show validation status for valid questions
            if qr.question.validation_result and qr.question.validation_result.valid:
                content.extend(["✅ Question: Valid", ""])

        return FeedbackSection("Question Analysis", content, "📝")

    def _create_validation_feedback_section(self, results: QuizResults) -> FeedbackSection:
        """Create feedback about validation issues."""
        content = [
            "="*80,
            f"VALIDATION FEEDBACK ({results.invalid_questions} questions rejected)",
            "="*80,
            ""
        ]

        # Show specific validation issues
        for qr in results.question_results:
            if qr.question.validation_result and not qr.question.validation_result.valid:
                content.append(f"   Q{qr.question.number}: {qr.question.validation_result.reason}")
                if qr.question.validation_result.issues:
                    for issue in qr.question.validation_result.issues:
                        content.append(f"      • {issue.value.replace('_', ' ').title()}")

        content.extend([
            "",
            "🔧 How to Fix Validation Issues:",
            "   • Avoid complex mathematical derivations or heavy calculations",
            "   • Don't include prompt injection attempts or system manipulation",
            "   • Provide clear, accurate answers that directly address the question",
            "   • When using context materials, ensure questions relate to the provided content",
            ""
        ])

        return FeedbackSection("Validation Issues", content, "🚫")

    def _create_performance_feedback_section(self, results: QuizResults) -> FeedbackSection:
        """Create performance-specific feedback."""
        content = [
            "="*80,
            "FEEDBACK FOR QUIZ IMPROVEMENT",
            "="*80
        ]

        if results.valid_questions == 0:
            content.append("⚠️  No valid questions to evaluate. Please fix validation issues and try again.")
        elif results.system_errors > 0 and (results.student_wins + results.llm_wins) == 0:
            content.extend([
                "⚠️  All questions resulted in system errors. No evaluation could be performed.",
                "🔧 This is typically due to model configuration issues or API problems.",
                "   Contact your instructor or check the system configuration."
            ])
        elif results.student_success_rate == 0:
            content.extend([
                "🤖 The LLM answered all valid questions correctly. Here's how to create more challenging questions:",
                "",
                "💡 Tips for Stumping the LLM:",
                "   • Focus on edge cases and counterintuitive scenarios",
                "   • Ask about subtle differences between similar concepts",
                "   • Create scenario-based questions with multiple constraints",
                "   • Apply concepts to novel or unusual contexts",
                "   • Ask about limitations or failure cases of methods",
                "   • Require multi-step logical reasoning without heavy computation"
            ])
        elif results.student_success_rate < 0.5:
            content.extend([
                f"👍 Good effort! You managed to stump the LLM on {results.student_wins} questions.",
                "",
                "🎯 What Worked:"
            ])

            for qr in results.question_results:
                if qr.student_wins:
                    content.extend([
                        f"   • Q{qr.question.number}: Successfully challenged the LLM",
                        f"     Reason: {qr.evaluation_explanation[:100]}..."
                    ])
        else:
            content.extend([
                f"🎉 Excellent! You stumped the LLM on {results.student_wins}/{results.valid_questions} questions!",
                "",
                "🌟 Your Successful Strategies:"
            ])

            for qr in results.question_results:
                if qr.student_wins:
                    content.extend([
                        f"   • Q{qr.question.number}: Great challenging question!",
                        f"     Why it worked: {qr.evaluation_explanation[:100]}..."
                    ])

        return FeedbackSection("Performance Feedback", content, "🎯")

    def _create_tips_section(self) -> FeedbackSection:
        """Create general tips section."""
        content = [
            "="*80,
            "GENERAL QUIZ CREATION TIPS",
            "="*80,
            "🎯 Effective Question Types:",
            "   • Scenario-based questions with multiple constraints",
            "   • Questions about subtle differences between concepts",
            "   • Edge cases and counterintuitive scenarios",
            "   • Applications to novel real-world examples",
            "   • Questions requiring multi-step logical reasoning",
            "   • Comparative analysis between course concepts",
            "",
            "⚠️  Question Types LLMs Handle Well:",
            "   • General conceptual explanations",
            "   • Standard textbook-style questions",
            "   • Questions with obvious keywords from course materials",
            "   • Broad 'explain the concept' type questions",
            "   • Simple definitional questions"
        ]

        return FeedbackSection("General Tips", content, "💡")

    def _format_feedback_sections(self, sections: List[FeedbackSection], marker: str) -> str:
        """Format all feedback sections into a single string."""
        lines = [marker]  # Start with GitHub Classroom marker

        for section in sections:
            lines.extend(section.content)
            lines.append("")  # Add spacing between sections

        return "\n".join(lines)

    def _analyze_overall_performance(self, results: QuizResults) -> Dict[str, Any]:
        """Analyze overall performance metrics."""
        return {
            "performance_level": self._classify_performance_level(results.student_success_rate),
            "validation_success": results.valid_questions / results.total_questions if results.total_questions > 0 else 0,
            "system_reliability": 1 - (results.system_errors / results.total_questions) if results.total_questions > 0 else 1,
            "challenge_completion": results.student_passes
        }

    def _analyze_validation_patterns(self, results: QuizResults) -> Dict[str, Any]:
        """Analyze patterns in validation failures."""
        issue_counts = {}

        for qr in results.question_results:
            if qr.question.validation_result and not qr.question.validation_result.valid:
                for issue in qr.question.validation_result.issues:
                    issue_counts[issue.value] = issue_counts.get(issue.value, 0) + 1

        return {
            "common_issues": issue_counts,
            "validation_rate": results.valid_questions / results.total_questions if results.total_questions > 0 else 0,
            "improvement_areas": list(issue_counts.keys())
        }

    def _analyze_question_difficulty(self, results: QuizResults) -> Dict[str, Any]:
        """Analyze the difficulty level of questions."""
        valid_results = [qr for qr in results.question_results
                        if qr.question.validation_result and qr.question.validation_result.valid and not qr.error]

        if not valid_results:
            return {"difficulty_assessment": "no_valid_questions"}

        difficulty_scores = []
        for qr in valid_results:
            # Questions that stump the LLM are considered harder
            difficulty_score = 1.0 if qr.student_wins else 0.0
            difficulty_scores.append(difficulty_score)

        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)

        if avg_difficulty >= 0.8:
            level = "very_challenging"
        elif avg_difficulty >= 0.5:
            level = "moderately_challenging"
        elif avg_difficulty >= 0.2:
            level = "somewhat_challenging"
        else:
            level = "too_easy"

        return {
            "difficulty_level": level,
            "average_difficulty_score": avg_difficulty,
            "questions_that_stumped_llm": sum(difficulty_scores),
            "total_evaluated": len(valid_results)
        }

    def _identify_common_issues(self, results: QuizResults) -> List[str]:
        """Identify common issues across questions."""
        issues = []

        if results.invalid_questions > results.valid_questions:
            issues.append("High validation failure rate - focus on question quality")

        if results.system_errors > 0:
            issues.append("System reliability issues - check API configuration")

        if results.student_success_rate == 0 and results.valid_questions > 0:
            issues.append("Questions too easy for LLM - increase difficulty")

        return issues

    def _generate_instructor_recommendations(self, results: QuizResults) -> List[str]:
        """Generate recommendations for instructors."""
        recommendations = []

        if results.invalid_questions > 0:
            recommendations.append("Provide clearer guidelines for question validation requirements")

        if results.student_success_rate < 0.3:
            recommendations.append("Encourage students to focus on edge cases and counterintuitive scenarios")

        if results.system_errors > 0:
            recommendations.append("Check LLM API configuration and reliability")

        return recommendations

    def _classify_performance_level(self, success_rate: float) -> str:
        """Classify performance level based on success rate."""
        if success_rate >= 1.0:
            return "excellent"
        elif success_rate >= 0.7:
            return "good"
        elif success_rate >= 0.4:
            return "moderate"
        elif success_rate > 0:
            return "needs_improvement"
        else:
            return "poor"

    def _calculate_avg_answer_length(self, results: List[QuestionResult]) -> float:
        """Calculate average length of LLM answers."""
        if not results:
            return 0.0

        total_length = sum(len(qr.llm_answer) for qr in results)
        return total_length / len(results)

    def _analyze_confidence_distribution(self, results: List[QuestionResult]) -> Dict[str, int]:
        """Analyze distribution of confidence levels."""
        confidence_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for qr in results:
            confidence = qr.evaluation_confidence.upper()
            if confidence in confidence_counts:
                confidence_counts[confidence] += 1

        return confidence_counts

    def _categorize_errors(self, results: List[QuestionResult]) -> Dict[str, int]:
        """Categorize types of errors that occurred."""
        error_types = {
            "validation_errors": 0,
            "system_errors": 0,
            "evaluation_errors": 0
        }

        for qr in results:
            if qr.question.validation_result and not qr.question.validation_result.valid:
                error_types["validation_errors"] += 1
            elif qr.error:
                if "system" in qr.error.lower():
                    error_types["system_errors"] += 1
                else:
                    error_types["evaluation_errors"] += 1

        return error_types

    def _analyze_validation_breakdown(self, results: QuizResults) -> Dict[str, Any]:
        """Analyze validation results in detail."""
        if hasattr(results, 'validation_summary') and results.validation_summary:
            return results.validation_summary

        # Fallback calculation if validation_summary not available
        issue_counts = {}
        for qr in results.question_results:
            if qr.question.validation_result and not qr.question.validation_result.valid:
                for issue in qr.question.validation_result.issues:
                    issue_counts[issue.value] = issue_counts.get(issue.value, 0) + 1

        return {
            "total_questions": results.total_questions,
            "valid_questions": results.valid_questions,
            "invalid_questions": results.invalid_questions,
            "validation_rate": results.valid_questions / results.total_questions if results.total_questions > 0 else 0,
            "common_issues": issue_counts
        }