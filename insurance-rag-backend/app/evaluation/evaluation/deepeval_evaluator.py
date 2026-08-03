# src/evaluation/deepeval_evaluator.py
import json
import os
import re
from typing import List
from openai import OpenAI

class SimpleRAGEvaluator:
    """Simple RAG evaluator using DeepSeek - No external libraries needed"""
    
    def __init__(self, rag_search_function, llm_answer_function, api_key=None):
        self.rag_search = rag_search_function
        self.llm_answer = llm_answer_function
        
        # Use provided API key or get from environment
        if api_key is None:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def load_test_questions(self, file_path="src/evaluation/test_dataset.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data["questions"]
        except:
            return [
                "What is the deductible for collision coverage?",
                "Does my renters policy cover laptop theft?",
                "What are my auto liability limits?"
            ]
    
    def evaluate_answer_relevancy(self, question: str, answer: str) -> float:
        """Evaluate if answer is relevant to the question"""
        prompt = f"""Rate how relevant this answer is to the question on a scale of 0.0 to 1.0.

Question: {question}
Answer: {answer}

Rate ONLY a number between 0.0 and 1.0 where:
- 1.0 = Perfectly relevant, fully answers the question
- 0.7 = Mostly relevant, covers main points
- 0.5 = Partially relevant, misses key points
- 0.0 = Completely irrelevant

Return ONLY the number, nothing else:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip()
            numbers = re.findall(r'(\d+\.?\d*)', result)
            if numbers:
                return min(1.0, max(0.0, float(numbers[0])))
            return 0.5
        except Exception as e:
            print(f"      Error in relevancy: {e}")
            return 0.5
    
    def evaluate_faithfulness(self, question: str, answer: str, contexts: List[str]) -> float:
        """Evaluate if answer is faithful to the retrieved contexts"""
        context_text = "\n".join(contexts[:3])
        
        prompt = f"""Rate how faithful this answer is to the provided context on a scale of 0.0 to 1.0.

CONTEXT (from policy documents):
{context_text}

QUESTION: {question}
ANSWER: {answer}

Rate ONLY a number between 0.0 and 1.0 where:
- 1.0 = Perfect, ALL claims in answer are supported by context
- 0.7 = Most claims supported, minor hallucinations
- 0.5 = Some claims not supported by context
- 0.0 = Answer completely made up, nothing from context

Return ONLY the number, nothing else:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip()
            numbers = re.findall(r'(\d+\.?\d*)', result)
            if numbers:
                return min(1.0, max(0.0, float(numbers[0])))
            return 0.5
        except Exception as e:
            print(f"      Error in faithfulness: {e}")
            return 0.5
    
    def run_evaluation(self, questions: List[str] = None):
        if questions is None:
            questions = self.load_test_questions()
        
        print(f"\n📊 Running RAG Evaluation on {len(questions)} questions...")
        print("-" * 50)
        
        results = []
        
        for i, question in enumerate(questions):
            print(f"\n  [{i+1}/{len(questions)}] {question[:60]}...")
            
            # Run RAG
            search_results, _ = self.rag_search(question, k=3)
            answer, _ = self.llm_answer(question, search_results)
            contexts = [r.get("text", "")[:500] for r in search_results[:3]]
            
            print(f"      Answer length: {len(answer)} chars")
            
            # Evaluate
            relevancy = self.evaluate_answer_relevancy(question, answer)
            faithfulness = self.evaluate_faithfulness(question, answer, contexts)
            
            results.append({
                "question": question,
                "answer": answer[:200] + "...",
                "answer_relevancy": relevancy,
                "faithfulness": faithfulness
            })
            
            print(f"      Answer Relevancy: {relevancy:.2%}")
            print(f"      Faithfulness: {faithfulness:.2%}")
        
        # Calculate averages
        avg_relevancy = sum(r["answer_relevancy"] for r in results) / len(results)
        avg_faithfulness = sum(r["faithfulness"] for r in results) / len(results)
        
        # Print report
        print("\n" + "="*50)
        print("📊 RAG EVALUATION REPORT")
        print("="*50)
        print(f"\n📈 Average Answer Relevancy: {avg_relevancy:.2%}")
        print(f"📈 Average Faithfulness: {avg_faithfulness:.2%}")
        print(f"\n📊 Overall Score: {(avg_relevancy + avg_faithfulness)/2:.2%}")
        
        print("\n📋 Detailed Results:")
        for r in results:
            print(f"\n   Q: {r['question'][:50]}...")
            print(f"   → Relevancy: {r['answer_relevancy']:.2%}, Faithfulness: {r['faithfulness']:.2%}")
        
        print("\n" + "="*50)
        print("💡 Interpretation:")
        if avg_faithfulness < 0.7:
            print("   ⚠️ Faithfulness is low - AI may be hallucinating!")
        else:
            print("   ✅ Faithfulness is good - AI stays true to documents")
        
        if avg_relevancy > 0.8:
            print("   ✅ Answer relevancy is excellent")
        elif avg_relevancy > 0.6:
            print("   📈 Answer relevancy is acceptable")
        else:
            print("   ⚠️ Answer relevancy needs improvement")
        
        print("="*50)
        
        # Save report
        report = {
            "average_answer_relevancy": avg_relevancy,
            "average_faithfulness": avg_faithfulness,
            "overall_score": (avg_relevancy + avg_faithfulness) / 2,
            "individual_results": results
        }
        
        with open("rag_evaluation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("\n✅ Report saved to rag_evaluation_report.json")
        
        return report
