"""
Notebook-friendly interface for the LLM Quiz Challenge.

This module provides a high-level, easy-to-use interface designed for
interactive environments like Marimo, Jupyter notebooks, and Python scripts.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from .llm_client import LLMClient
from .quiz_runner import QuizRunner, QuizResults, QuizQuestion
from .results_analyzer import ResultsAnalyzer

logger = logging.getLogger(__name__)


class LLMQuizChallenge:
    """
    High-level interface for running LLM quiz challenges.
    
    Designed for notebook environments and interactive use cases.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1",
                 quiz_model: str = "gpt-4o-mini", evaluator_model: str = "gpt-4o",
                 context_window_size: int = 32768, max_tokens: int = 500):
        """Initialize the quiz challenge system.
        
        Args:
            api_key: API key for LLM service
            base_url: Base URL for LLM API (default: OpenRouter)
            quiz_model: Model for answering questions (default: gpt-4o-mini)
            evaluator_model: Model for evaluating answers (default: gpt-4o)
            context_window_size: Context window size for models (default: 32768)
            max_tokens: Maximum tokens in LLM response (default: 500)
        """
        self.llm_client = LLMClient(base_url=base_url, api_key=api_key, 
                                   context_window_size=context_window_size)
        self.quiz_runner = QuizRunner(
            llm_client=self.llm_client,
            quiz_model=quiz_model,
            evaluator_model=evaluator_model,
            max_tokens=max_tokens
        )
        self.results_analyzer = ResultsAnalyzer()
        self.last_results: Optional[QuizResults] = None
        
        logger.info(f"Initialized LLM Quiz Challenge")
        logger.info(f"API: {base_url}")
        logger.info(f"Models: quiz={quiz_model}, evaluator={evaluator_model}")
    
    def load_context_from_urls_file(self, urls_file: str) -> bool:
        """Load context materials from a file containing URLs.
        
        Args:
            urls_file: Path to file with URLs (one per line)
            
        Returns:
            True if context was loaded successfully
        """
        return self.quiz_runner.load_context_from_urls_file(urls_file)
    
    def load_context_from_urls(self, urls: List[str]) -> bool:
        """Load context materials from a list of URLs.
        
        Args:
            urls: List of URLs to fetch content from
            
        Returns:
            True if context was loaded successfully
        """
        return self.quiz_runner.load_context_from_urls(urls)
    
    def run_quiz_from_file(self, quiz_file: Union[str, Path], 
                          quiz_title: str = None) -> QuizResults:
        """Run a quiz challenge from a TOML file.
        
        Args:
            quiz_file: Path to TOML quiz file
            quiz_title: Optional title for the quiz
            
        Returns:
            Complete quiz results
        """
        quiz_path = Path(quiz_file)
        if not quiz_title:
            quiz_title = quiz_path.stem.replace('_', ' ').title()
        
        questions = self.quiz_runner.load_quiz_from_file(quiz_path)
        self.last_results = self.quiz_runner.run_quiz_challenge(questions, quiz_title)
        
        return self.last_results
    
    def run_quiz_from_dict(self, quiz_data: Dict[str, Any], 
                          quiz_title: str = "Quiz Challenge") -> QuizResults:
        """Run a quiz challenge from a dictionary.
        
        Args:
            quiz_data: Dictionary with 'questions' key containing question data
            quiz_title: Title for the quiz
            
        Returns:
            Complete quiz results
        """
        questions = self.quiz_runner.load_quiz_from_dict(quiz_data)
        self.last_results = self.quiz_runner.run_quiz_challenge(questions, quiz_title)
        
        return self.last_results
    
    def run_quiz_from_questions(self, questions: List[Dict[str, str]], 
                               quiz_title: str = "Quiz Challenge") -> QuizResults:
        """Run a quiz challenge from a list of question dictionaries.
        
        Args:
            questions: List of dicts with 'question' and 'answer' keys
            quiz_title: Title for the quiz
            
        Returns:
            Complete quiz results
        """
        quiz_questions = []
        for i, q_data in enumerate(questions, 1):
            question = QuizQuestion(
                question=q_data.get('question', ''),
                answer=q_data.get('answer', ''),
                number=i
            )
            quiz_questions.append(question)
        
        self.last_results = self.quiz_runner.run_quiz_challenge(quiz_questions, quiz_title)
        return self.last_results
    
    def get_student_feedback(self, results: QuizResults = None) -> str:
        """Get formatted feedback for students.
        
        Args:
            results: Quiz results (uses last results if not provided)
            
        Returns:
            Formatted feedback string
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            return "No quiz results available. Please run a quiz first."
        
        return self.results_analyzer.generate_student_feedback(results)
    
    def get_instructor_summary(self, results: QuizResults = None) -> Dict[str, Any]:
        """Get instructor-focused summary and analysis.
        
        Args:
            results: Quiz results (uses last results if not provided)
            
        Returns:
            Dictionary with instructor analysis
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            return {"error": "No quiz results available. Please run a quiz first."}
        
        return self.results_analyzer.generate_instructor_summary(results)
    
    def get_detailed_statistics(self, results: QuizResults = None) -> Dict[str, Any]:
        """Get detailed statistics about quiz performance.
        
        Args:
            results: Quiz results (uses last results if not provided)
            
        Returns:
            Detailed statistics dictionary
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            return {"error": "No quiz results available. Please run a quiz first."}
        
        return self.results_analyzer.get_detailed_statistics(results)
    
    def save_results(self, output_file: Union[str, Path], results: QuizResults = None) -> None:
        """Save quiz results to a JSON file.
        
        Args:
            output_file: Path to output JSON file
            results: Quiz results (uses last results if not provided)
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            raise ValueError("No quiz results available. Please run a quiz first.")
        
        self.quiz_runner.save_results(results, Path(output_file))
    
    def print_summary(self, results: QuizResults = None) -> None:
        """Print a concise summary of quiz results.
        
        Args:
            results: Quiz results (uses last results if not provided)
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            print("No quiz results available. Please run a quiz first.")
            return
        
        print(f"\n📊 Quiz Summary: {results.quiz_title}")
        print("="*50)
        print(f"Total Questions: {results.total_questions}")
        print(f"Valid Questions: {results.valid_questions}")
        print(f"Student Success Rate: {results.student_success_rate:.1%}")
        print(f"Result: {'PASS ✅' if results.student_passes else 'FAIL ❌'}")
        
        if results.invalid_questions > 0:
            print(f"Invalid Questions: {results.invalid_questions}")
        
        if results.system_errors > 0:
            print(f"System Errors: {results.system_errors}")
    
    def display_question_results(self, results: QuizResults = None, show_details: bool = True) -> None:
        """Display results for each question in a notebook-friendly format.
        
        Args:
            results: Quiz results (uses last results if not provided)
            show_details: Whether to show detailed evaluation explanations
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            print("No quiz results available. Please run a quiz first.")
            return
        
        print(f"\n📝 Question-by-Question Results")
        print("="*60)
        
        for qr in results.question_results:
            # Handle invalid questions
            if qr.question.validation_result and not qr.question.validation_result.valid:
                print(f"\n❌ Question {qr.question.number}: INVALID")
                print(f"Question: {qr.question.question}")
                print(f"Issue: {qr.question.validation_result.reason}")
                continue
            
            # Handle system errors
            if qr.error:
                print(f"\n⚠️  Question {qr.question.number}: SYSTEM ERROR")
                print(f"Question: {qr.question.question}")
                print(f"Error: {qr.evaluation_explanation}")
                continue
            
            # Show successful evaluations
            winner_emoji = "🎉" if qr.student_wins else "🤖"
            winner = "Student" if qr.student_wins else "LLM"
            
            print(f"\n{winner_emoji} Question {qr.question.number}: {winner} wins")
            print(f"Question: {qr.question.question}")
            print(f"Expected: {qr.question.answer}")
            print(f"LLM Answer: {qr.llm_answer}")
            
            if show_details:
                print(f"Evaluation: {qr.evaluation_explanation}")
                print(f"Confidence: {qr.evaluation_confidence}")
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM API.
        
        Returns:
            True if connection successful
        """
        return self.llm_client.test_connection()
    
    def validate_questions_only(self, questions: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate questions without running the full challenge.
        
        Args:
            questions: List of dicts with 'question' and 'answer' keys
            
        Returns:
            Validation summary
        """
        validation_results = []
        
        for q_data in questions:
            result = self.quiz_runner.validator.validate_question(
                question=q_data.get('question', ''),
                answer=q_data.get('answer', ''),
                context_content=self.quiz_runner.context_content
            )
            validation_results.append(result)
        
        return self.quiz_runner.validator.get_validation_summary(validation_results)
    
    # Convenience methods for notebook workflows
    
    @classmethod
    def quick_setup(cls, api_key: str, context_window_size: int = 32768) -> 'LLMQuizChallenge':
        """Quick setup with default configuration.
        
        Args:
            api_key: API key for LLM service
            context_window_size: Context window size for models (default: 32768)
            
        Returns:
            Configured LLMQuizChallenge instance
        """
        return cls(api_key=api_key, context_window_size=context_window_size)
    
    def quick_run(self, quiz_file: Union[str, Path], context_urls: Optional[List[str]] = None) -> str:
        """Run a complete quiz challenge with minimal setup.
        
        Args:
            quiz_file: Path to TOML quiz file
            context_urls: Optional URLs for context materials
            
        Returns:
            Formatted student feedback
        """
        # Load context if provided
        if context_urls:
            self.load_context_from_urls(context_urls)
        
        # Run the quiz
        results = self.run_quiz_from_file(quiz_file)
        
        # Return formatted feedback
        return self.get_student_feedback(results)