"""
Quiz runner orchestration for the LLM Quiz Challenge.

This module orchestrates the complete quiz challenge process, coordinating
between validation, question answering, and evaluation components.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

try:
    import tomllib  # Python 3.11+ built-in TOML parser
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11

from .llm_client import LLMClient, LLMRequest, LLMMessage
from .content_loader import ContentLoader
from .validator import QuestionValidator, ValidationResult

logger = logging.getLogger(__name__)


class DataclassJSONEncoder(json.JSONEncoder):
    """JSON encoder that can handle dataclasses and enums."""
    
    def default(self, obj):
        if hasattr(obj, '__dataclass_fields__'):
            # Convert dataclass to dictionary
            return asdict(obj)
        elif hasattr(obj, 'value'):
            # Handle enums
            return obj.value
        elif hasattr(obj, 'name'):
            # Handle enums without value
            return obj.name
        return super().default(obj)


@dataclass
class QuizQuestion:
    """Represents a single quiz question with metadata."""
    question: str
    answer: str
    number: int
    validation_result: Optional[ValidationResult] = None


@dataclass
class QuestionResult:
    """Result of processing a single question through the quiz challenge."""
    question: QuizQuestion
    llm_answer: str
    is_correct: bool
    student_wins: bool
    evaluation_explanation: str
    evaluation_confidence: str
    raw_evaluation: Optional[str] = None
    error: Optional[str] = None


@dataclass
class QuizResults:
    """Complete results of a quiz challenge session."""
    total_questions: int
    valid_questions: int
    invalid_questions: int
    system_errors: int
    student_wins: int
    llm_wins: int
    student_success_rate: float
    question_results: List[QuestionResult]
    validation_summary: Dict[str, Any]
    quiz_title: str = "Quiz Challenge"
    quiz_model: str = ""
    evaluator_model: str = ""
    
    @property
    def student_passes(self) -> bool:
        """Whether the student passes the challenge (all questions must be valid)."""
        evaluated_questions = self.student_wins + self.llm_wins
        has_evaluated_questions = evaluated_questions > 0
        
        # All questions must be valid - no gaming allowed
        all_questions_valid = self.valid_questions == self.total_questions
        
        # Must have at least some questions to evaluate
        has_questions_to_evaluate = self.total_questions > 0
        
        return (has_questions_to_evaluate and 
                all_questions_valid and 
                has_evaluated_questions and 
                self.student_success_rate >= 1.0)


class QuizRunner:
    """Orchestrates the complete quiz challenge process."""
    
    def __init__(self, llm_client: LLMClient, quiz_model: str, evaluator_model: str, max_tokens: int = 500):
        """Initialize the quiz runner.
        
        Args:
            llm_client: LLM client for API interactions
            quiz_model: Model for answering quiz questions
            evaluator_model: Model for evaluating answers
            max_tokens: Maximum tokens in LLM response (default: 500)
        """
        self.llm_client = llm_client
        self.quiz_model = quiz_model
        self.evaluator_model = evaluator_model
        self.max_tokens = max_tokens
        self.content_loader = ContentLoader()
        self.validator = QuestionValidator(llm_client, evaluator_model, max_tokens)
        self.context_content: Optional[str] = None
    
    def _get_evaluation_schema(self) -> Dict[str, Any]:
        """Get JSON schema for structured evaluation responses."""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "evaluation_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "verdict": {
                            "type": "string",
                            "enum": ["CORRECT", "INCORRECT"],
                            "description": "Whether the LLM's answer is correct or incorrect"
                        },
                        "student_wins": {
                            "type": "boolean",
                            "description": "True if the student wins (LLM got it wrong), False if LLM got it right"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Brief explanation of the evaluation decision and reasoning"
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"],
                            "description": "Confidence level in the evaluation"
                        }
                    },
                    "required": ["verdict", "student_wins", "explanation", "confidence"],
                    "additionalProperties": False
                }
            }
        }
    
    def load_context_from_urls_file(self, urls_file: str) -> bool:
        """Load context content from a URLs file.
        
        Args:
            urls_file: Path to file containing URLs
            
        Returns:
            True if context was loaded successfully
        """
        self.context_content = self.content_loader.load_from_urls_file(urls_file)
        
        if self.context_content:
            logger.info(f"Context loaded: {len(self.context_content)} characters")
            return True
        else:
            logger.warning("No context content was loaded")
            return False
    
    def load_context_from_urls(self, urls: List[str]) -> bool:
        """Load context content from a list of URLs.
        
        Args:
            urls: List of URLs to fetch content from
            
        Returns:
            True if context was loaded successfully
        """
        self.context_content = self.content_loader.load_from_urls(urls)
        
        if self.context_content:
            logger.info(f"Context loaded: {len(self.context_content)} characters")
            return True
        else:
            logger.warning("No context content was loaded")
            return False
    
    def load_quiz_from_file(self, quiz_file: Path) -> List[QuizQuestion]:
        """Load quiz questions from a TOML file.
        
        Args:
            quiz_file: Path to TOML quiz file
            
        Returns:
            List of QuizQuestion objects
        """
        try:
            with open(quiz_file, 'rb') as f:
                quiz_data = tomllib.load(f)
            
            questions = []
            for i, q_data in enumerate(quiz_data.get('questions', []), 1):
                question = QuizQuestion(
                    question=q_data.get('question', ''),
                    answer=q_data.get('answer', ''),
                    number=i
                )
                questions.append(question)
            
            logger.info(f"Loaded {len(questions)} questions from {quiz_file}")
            return questions
            
        except Exception as e:
            logger.error(f"Error loading quiz file {quiz_file}: {e}")
            raise
    
    def load_quiz_from_dict(self, quiz_data: Dict[str, Any]) -> List[QuizQuestion]:
        """Load quiz questions from a dictionary.
        
        Args:
            quiz_data: Dictionary with 'questions' key containing question data
            
        Returns:
            List of QuizQuestion objects
        """
        questions = []
        for i, q_data in enumerate(quiz_data.get('questions', []), 1):
            question = QuizQuestion(
                question=q_data.get('question', ''),
                answer=q_data.get('answer', ''),
                number=i
            )
            questions.append(question)
        
        logger.info(f"Loaded {len(questions)} questions from dictionary")
        return questions
    
    def run_quiz_challenge(self, questions: List[QuizQuestion], 
                          quiz_title: str = "Quiz Challenge") -> QuizResults:
        """Run the complete quiz challenge process.
        
        Args:
            questions: List of quiz questions
            quiz_title: Title for the quiz
            
        Returns:
            Complete quiz results
        """
        logger.info(f"Starting quiz challenge with {len(questions)} questions")
        
        # Initialize results tracking
        question_results = []
        valid_count = 0
        student_wins = 0
        llm_wins = 0
        system_errors = 0
        
        # Validate all questions first
        validation_results = []
        for question in questions:
            validation_result = self.validator.validate_question(
                question.question, 
                question.answer, 
                self.context_content
            )
            question.validation_result = validation_result
            validation_results.append(validation_result)
            
            if validation_result.valid:
                valid_count += 1
        
        # Process each question
        for question in questions:
            logger.info(f"Processing question {question.number}: {question.question[:50]}...")
            
            # Handle invalid questions - include them in results with detailed validation info
            if not question.validation_result.valid:
                # Create result for invalid question with detailed validation explanation
                invalid_reason_details = []
                for issue in question.validation_result.issues:
                    if issue.value == "context_mismatch":
                        invalid_reason_details.append("The question does not relate to the provided context materials (small-world networks lecture content)")
                    elif issue.value == "heavy_math":
                        invalid_reason_details.append("The question requires complex mathematical derivations or extensive calculations")
                    elif issue.value == "prompt_injection":
                        invalid_reason_details.append("The question contains attempts to manipulate the AI system")
                    elif issue.value == "answer_quality":
                        invalid_reason_details.append("The provided answer appears to be incorrect or poorly formed")
                
                detailed_reason = f"{question.validation_result.reason}"
                if invalid_reason_details:
                    detailed_reason += f" Specific issues: {'; '.join(invalid_reason_details)}"
                
                logger.warning(f"Question {question.number} REJECTED - {detailed_reason}")
                print(f"\n❌ QUESTION {question.number} REJECTED")
                print(f"Question: {question.question}")
                print(f"Reason: {detailed_reason}")
                if question.validation_result.issues:
                    print(f"Issues found: {[issue.value for issue in question.validation_result.issues]}")
                print(f"Confidence: {question.validation_result.confidence.upper()}")
                print("-" * 60)
                
                result = QuestionResult(
                    question=question,
                    llm_answer="Question rejected during validation",
                    is_correct=False,
                    student_wins=False,
                    evaluation_explanation=f"INVALID QUESTION: {detailed_reason}",
                    evaluation_confidence="HIGH",
                    error=f"Validation failed: {detailed_reason}"
                )
                question_results.append(result)
                continue
            
            # Get LLM answer
            llm_response = self._get_llm_answer(question.question)
            
            if not llm_response.success:
                logger.error(f"Failed to get LLM answer for question {question.number}: {llm_response.error}")
                system_errors += 1
                
                result = QuestionResult(
                    question=question,
                    llm_answer="System error - no response",
                    is_correct=False,
                    student_wins=False,
                    evaluation_explanation=f"System error: {llm_response.error}",
                    evaluation_confidence="HIGH",
                    error=llm_response.error
                )
                question_results.append(result)
                continue
            
            # Evaluate the answer
            evaluation = self._evaluate_answer(question.question, question.answer, llm_response.content)
            
            if not evaluation.success:
                logger.error(f"Failed to evaluate question {question.number}: {evaluation.error}")
                system_errors += 1
                
                result = QuestionResult(
                    question=question,
                    llm_answer=llm_response.content,
                    is_correct=False,
                    student_wins=False,
                    evaluation_explanation=f"Evaluation error: {evaluation.error}",
                    evaluation_confidence="LOW",
                    error=evaluation.error
                )
                question_results.append(result)
                continue
            
            # Parse structured JSON response
            try:
                eval_data = json.loads(evaluation.content)
                
                verdict = eval_data.get("verdict", "INCORRECT")
                question_student_wins = eval_data.get("student_wins", False)
                explanation = eval_data.get("explanation", "No explanation provided")
                confidence = eval_data.get("confidence", "MEDIUM")
                
                is_correct = verdict == "CORRECT"
                
                if question_student_wins:
                    student_wins += 1
                else:
                    llm_wins += 1
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse structured evaluation response: {e}")
                logger.error(f"Raw response: {evaluation.content}")
                
                # Fallback to treating as system error
                system_errors += 1
                result = QuestionResult(
                    question=question,
                    llm_answer=llm_response.content,
                    is_correct=False,
                    student_wins=False,
                    evaluation_explanation=f"Evaluation parsing error: {evaluation.content}",
                    evaluation_confidence="LOW",
                    error=f"JSON parsing failed: {e}"
                )
                question_results.append(result)
                continue
            
            result = QuestionResult(
                question=question,
                llm_answer=llm_response.content,
                is_correct=is_correct,
                student_wins=question_student_wins,
                evaluation_explanation=explanation,
                evaluation_confidence=confidence,
                raw_evaluation=evaluation.content
            )
            question_results.append(result)
        
        # Calculate final results
        evaluated_questions = student_wins + llm_wins
        success_rate = student_wins / evaluated_questions if evaluated_questions > 0 else 0.0
        
        # Generate validation summary
        validation_summary = self.validator.get_validation_summary(validation_results)
        
        # Print summary of rejected questions
        rejected_questions = [qr for qr in question_results if "INVALID QUESTION" in qr.evaluation_explanation]
        if rejected_questions:
            print(f"\n{'='*80}")
            print(f"VALIDATION SUMMARY: {len(rejected_questions)} QUESTION(S) REJECTED")
            print(f"{'='*80}")
            for qr in rejected_questions:
                print(f"Question {qr.question.number}: {qr.question.question[:100]}...")
                print(f"Rejection reason: {qr.evaluation_explanation.replace('INVALID QUESTION: ', '')}")
                print("-" * 40)
        
        return QuizResults(
            total_questions=len(questions),
            valid_questions=valid_count,
            invalid_questions=len(questions) - valid_count,
            system_errors=system_errors,
            student_wins=student_wins,
            llm_wins=llm_wins,
            student_success_rate=success_rate,
            question_results=question_results,
            validation_summary=validation_summary,
            quiz_title=quiz_title,
            quiz_model=self.quiz_model,
            evaluator_model=self.evaluator_model
        )
    
    def _get_llm_answer(self, question: str) -> Any:
        """Get LLM answer to a quiz question."""
        if self.context_content:
            system_message = f"""You are a student taking a quiz. You have been provided with context materials below. Use this content to answer questions accurately.

{self.context_content}

Instructions:
- Answer questions based on the context materials provided above
- Be concise but thorough in your explanations. No more than 300 words.
- Use the concepts and terminology from the provided materials
- If you're unsure about something, refer back to the provided content
- Do not ask for clarification - provide your best answer based on the information available"""
        else:
            system_message = ("You are a student taking a quiz. "
                             "Answer the questions to the best of your ability. "
                             "Be concise but thorough in your explanations. "
                             "Do not ask for clarification - provide your best answer.")
        
        prompt = f"Question: {question}\n\nPlease provide your answer:"
        
        return self.llm_client.simple_chat(
            prompt=prompt,
            model=self.quiz_model,
            system_message=system_message,
            temperature=0.1,
            max_tokens=self.max_tokens
        )
    
    def _evaluate_answer(self, question: str, correct_answer: str, llm_answer: str) -> Any:
        """Evaluate LLM answer against the correct answer using structured output."""
        system_message = ("You are an expert evaluator for academic questions. "
                         "Your job is to determine if a student's answer is correct or incorrect. "
                         "Be strict but fair in your evaluation. "
                         "Respond with structured JSON containing your evaluation.")
        
        prompt = f"""Evaluate whether the following answer is correct or incorrect.

QUESTION:
{question}

CORRECT ANSWER (provided by student):
{correct_answer}

LLM's ANSWER:
{llm_answer}

Consider the answer correct if it demonstrates understanding of the core concepts, even if the wording is different from the student's answer. Consider it incorrect if there are errors, missing key points, or fundamental misunderstandings.

Your response must include:
- verdict: "CORRECT" or "INCORRECT" 
- student_wins: true if LLM got it wrong (student wins), false if LLM got it right
- explanation: Brief explanation of your decision and reasoning
- confidence: "HIGH", "MEDIUM", or "LOW" confidence in your evaluation"""
        
        return self.llm_client.simple_chat(
            prompt=prompt,
            model=self.evaluator_model,
            system_message=system_message,
            temperature=0.1,
            max_tokens=self.max_tokens,
            response_format=self._get_evaluation_schema()
        )
    
    def save_results(self, results: QuizResults, output_file: Path) -> None:
        """Save quiz results to a JSON file.
        
        Args:
            results: Quiz results to save
            output_file: Path to output JSON file
        """
        try:
            # Convert dataclasses to dictionaries for JSON serialization
            results_dict = {
                "quiz_title": results.quiz_title,
                "quiz_model": results.quiz_model,
                "evaluator_model": results.evaluator_model,
                "total_questions": results.total_questions,
                "valid_questions": results.valid_questions,
                "invalid_questions": results.invalid_questions,
                "system_errors": results.system_errors,
                "student_wins": results.student_wins,
                "llm_wins": results.llm_wins,
                "student_success_rate": results.student_success_rate,
                "student_passes": results.student_passes,
                "github_classroom_result": "STUDENTS_QUIZ_KEIKO_WIN" if results.student_passes else "STUDENTS_QUIZ_KEIKO_LOSE",
                "question_results": [
                    {
                        "question_number": qr.question.number,
                        "question": qr.question.question,
                        "correct_answer": qr.question.answer,
                        "llm_answer": qr.llm_answer,
                        "is_correct": qr.is_correct,
                        "student_wins": qr.student_wins,
                        "evaluation_explanation": qr.evaluation_explanation,
                        "evaluation_confidence": qr.evaluation_confidence,
                        "validation": {
                            "valid": qr.question.validation_result.valid if qr.question.validation_result else False,
                            "issues": [issue.value for issue in qr.question.validation_result.issues] if qr.question.validation_result else [],
                            "reason": qr.question.validation_result.reason if qr.question.validation_result else ""
                        },
                        "error": qr.error
                    }
                    for qr in results.question_results
                ],
                "validation_summary": results.validation_summary
            }
            
            with open(output_file, 'w') as f:
                json.dump(results_dict, f, indent=2, cls=DataclassJSONEncoder)
            
            logger.info(f"Results saved to {output_file}")
            
            # Log the pass criteria for clarity
            if results.student_passes:
                logger.info("✅ STUDENT PASSED - All questions valid and 100% win rate achieved")
            else:
                all_questions_valid = results.valid_questions == results.total_questions
                validation_rate = results.valid_questions / results.total_questions if results.total_questions > 0 else 0.0
                perfect_wins = results.student_success_rate >= 1.0
                
                logger.info(f"❌ STUDENT FAILED - Criteria check:")
                logger.info(f"   ✓ All questions valid: {all_questions_valid} ({results.valid_questions}/{results.total_questions})")
                logger.info(f"   ✓ 100% win rate: {perfect_wins} ({results.student_success_rate:.1%})")
                
                if not all_questions_valid:
                    invalid_count = results.total_questions - results.valid_questions
                    logger.info(f"   📝 {invalid_count} question(s) were rejected during validation")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise