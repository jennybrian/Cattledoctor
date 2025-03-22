import joblib
import pandas as pd
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import json
from datetime import datetime
import random

class ModelTester:
    def __init__(self, model_dir=None):
        """Initialize the model tester
        
        Args:
            model_dir: Optional path to model directory, defaults to script's parent directory
        """
        self.model_dir = Path(model_dir) if model_dir else Path(__file__).parent
        self.load_models()
        self.test_results = []
        
    def load_models(self):
        """Load all required ML models and preprocessors"""
        try:
            self.model = joblib.load(self.model_dir / 'cattle_disease_model.pkl')
            self.vectorizer = joblib.load(self.model_dir / 'description_vectorizer.pkl')
            self.label_encoder = joblib.load(self.model_dir / 'disease_label_encoder.pkl')
            print("✅ Models loaded successfully")
            
            # Get list of all disease names the model knows
            self.disease_classes = self.label_encoder.classes_
            print(f"📋 Model can diagnose {len(self.disease_classes)} different diseases")
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            raise

    def diagnose(self, symptoms, return_all_probabilities=False):
        """Diagnose disease with given symptoms
        
        Args:
            symptoms: List of symptoms
            return_all_probabilities: Whether to return all disease probabilities
            
        Returns:
            Dictionary of diagnosis results
        """
        try:
            # Prepare input
            symptoms_text = ', '.join(symptoms)
            
            # Transform input
            X = self.vectorizer.transform([symptoms_text])
            
            # Get predictions
            probabilities = self.model.predict_proba(X)[0]
            
            # If requested, return all probabilities
            if return_all_probabilities:
                all_probs = {
                    self.label_encoder.inverse_transform([i])[0]: float(prob) 
                    for i, prob in enumerate(probabilities)
                }
                return all_probs
            
            # Get top probabilities
            top_indices = probabilities.argsort()[-5:][::-1]  # Get top 5 instead of just 3
            
            results = []
            for idx in top_indices:
                if probabilities[idx] > 0.05:  # Lower threshold to 5% to catch more diseases
                    disease = self.label_encoder.inverse_transform([idx])[0]
                    confidence = probabilities[idx]
                    results.append({
                        'disease': disease,
                        'confidence': float(confidence)
                    })
            
            return results
                    
        except Exception as e:
            print(f"❌ Error during diagnosis: {str(e)}")
            return None
    
    def test_diagnosis(self, symptoms, verbose=True):
        """Test disease diagnosis with given symptoms and print results
        
        Args:
            symptoms: List of symptoms
            verbose: Whether to print detailed results
            
        Returns:
            List of diagnosis results
        """
        try:
            results = self.diagnose(symptoms)
            
            if verbose:
                print("\n🔍 Diagnosis Results:")
                print("-------------------")
                
                for result in results:
                    print(f"\n🦠 Disease: {result['disease']}")
                    print(f"✓ Confidence: {result['confidence']:.2%}")
                    print("-------------------")
            
            return results
                    
        except Exception as e:
            print(f"\n❌ Error during diagnosis: {str(e)}")
            return None
    
    def run_test_suite(self, test_cases, verbose=True):
        """Run a full test suite
        
        Args:
            test_cases: List of test case dictionaries
            verbose: Whether to print detailed results
            
        Returns:
            Dictionary with test results
        """
        if verbose:
            print("🐄 Testing Cattle Disease Diagnosis Model")
            print("=======================================")

        success_count = 0
        detailed_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            if verbose:
                print(f"\n📋 Test Case {i}: {test_case.get('category', 'Uncategorized')}")
                print(f"Symptoms: {', '.join(test_case['symptoms'])}")
                print(f"Expected: {test_case['expected']}")
            
            results = self.test_diagnosis(test_case['symptoms'], verbose)
            
            test_passed = False
            top_prediction = None
            confidence = 0
            
            if results:
                top_prediction = results[0]['disease']
                confidence = results[0]['confidence']
                
                # Check if expected disease is in top result
                if top_prediction == test_case['expected']:
                    test_passed = True
                    success_count += 1
                    
                    if verbose:
                        print("✅ Test Passed")
                else:
                    if verbose:
                        print("❌ Test Failed")
                        
                # Get rank of expected disease
                expected_found = False
                expected_rank = -1
                expected_confidence = 0
                
                for i, res in enumerate(results):
                    if res['disease'] == test_case['expected']:
                        expected_found = True
                        expected_rank = i + 1  # 1-based rank
                        expected_confidence = res['confidence']
                        break
            else:
                if verbose:
                    print("❌ Test Failed (No results returned)")
            
            # Store detailed results
            result_entry = {
                'category': test_case.get('category', 'Uncategorized'),
                'symptoms': test_case['symptoms'],
                'expected': test_case['expected'],
                'top_prediction': top_prediction,
                'top_confidence': confidence,
                'passed': test_passed,
                'expected_in_results': expected_found if results else False,
                'expected_rank': expected_rank,
                'expected_confidence': expected_confidence
            }
            
            detailed_results.append(result_entry)
            self.test_results.append(result_entry)
        
        # Print summary
        if verbose:
            print("\n📊 Test Summary")
            print(f"Passed: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")
        
        return {
            'total_tests': len(test_cases),
            'passed': success_count,
            'accuracy': success_count/len(test_cases),
            'detailed_results': detailed_results
        }
    
    def get_confusion_matrix(self):
        """Generate confusion matrix from test results
        
        Returns:
            Tuple of (matrix, labels)
        """
        if not self.test_results:
            print("No test results available")
            return None, None
        
        # Get unique diseases from test results
        expected_diseases = [r['expected'] for r in self.test_results]
        predicted_diseases = [r['top_prediction'] for r in self.test_results if r['top_prediction']]
        unique_diseases = sorted(list(set(expected_diseases + predicted_diseases)))
        
        # Create confusion matrix
        y_true = [r['expected'] for r in self.test_results]
        y_pred = [r['top_prediction'] if r['top_prediction'] else 'unknown' for r in self.test_results]
        
        cm = confusion_matrix(y_true, y_pred, labels=unique_diseases)
        
        return cm, unique_diseases
    
    def plot_confusion_matrix(self, save_path=None):
        """Plot confusion matrix
        
        Args:
            save_path: Optional path to save the plot
        """
        cm, labels = self.get_confusion_matrix()
        
        if cm is None:
            return
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=labels, yticklabels=labels)
        plt.xlabel('Predicted Disease')
        plt.ylabel('True Disease')
        plt.title('Confusion Matrix')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"📊 Confusion matrix saved to {save_path}")
        
        plt.show()
    
    def generate_report(self, output_dir="test_results"):
        """Generate comprehensive test report
        
        Args:
            output_dir: Directory to save reports
        """
        if not self.test_results:
            print("No test results available")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate overall metrics
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        accuracy = passed / total if total > 0 else 0
        
        # Category performance
        categories = {}
        for result in self.test_results:
            cat = result.get('category', 'Uncategorized')
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
        
        for cat in categories:
            categories[cat]['accuracy'] = (
                categories[cat]['passed'] / categories[cat]['total'] 
                if categories[cat]['total'] > 0 else 0
            )
        
        # Detailed metrics by disease
        diseases = {}
        for result in self.test_results:
            expected = result['expected']
            if expected not in diseases:
                diseases[expected] = {'total': 0, 'passed': 0, 'confidence_sum': 0}
            
            diseases[expected]['total'] += 1
            if result['passed']:
                diseases[expected]['passed'] += 1
                diseases[expected]['confidence_sum'] += result['top_confidence']
        
        for disease in diseases:
            diseases[disease]['accuracy'] = (
                diseases[disease]['passed'] / diseases[disease]['total'] 
                if diseases[disease]['total'] > 0 else 0
            )
            diseases[disease]['avg_confidence'] = (
                diseases[disease]['confidence_sum'] / diseases[disease]['passed'] 
                if diseases[disease]['passed'] > 0 else 0
            )
        
        # Generate classification report
        y_true = [r['expected'] for r in self.test_results]
        y_pred = [r['top_prediction'] if r['top_prediction'] else 'unknown' for r in self.test_results]
        report = classification_report(y_true, y_pred, output_dict=True)
        
        # Combine everything into a report
        full_report = {
            'timestamp': timestamp,
            'overall': {
                'total_tests': total,
                'passed': passed,
                'accuracy': accuracy
            },
            'category_performance': categories,
            'disease_performance': diseases,
            'classification_report': report,
            'detailed_results': self.test_results
        }
        
        # Save as JSON
        report_path = os.path.join(output_dir, f"test_report_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print(f"📝 Complete test report saved to {report_path}")
        
        # Save confusion matrix
        cm_path = os.path.join(output_dir, f"confusion_matrix_{timestamp}.png")
        self.plot_confusion_matrix(save_path=cm_path)
        
        # Print summary to console
        print("\n📊 Test Report Summary")
        print("====================")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({accuracy:.2%})")
        print("\nCategory Performance:")
        for cat, metrics in categories.items():
            print(f"- {cat}: {metrics['passed']}/{metrics['total']} ({metrics['accuracy']:.2%})")
        
        return full_report
    
    def analyze_symptom_impact(self, symptoms, expected_disease, variations=5):
        """Analyze the impact of individual symptoms on diagnosis
        
        Args:
            symptoms: List of baseline symptoms
            expected_disease: Expected disease
            variations: Number of symptom variations to test
            
        Returns:
            Dictionary with analysis results
        """
        print(f"🔍 Analyzing impact of symptoms for: {expected_disease}")
        print(f"Baseline symptoms: {', '.join(symptoms)}")
        
        # Get baseline diagnosis
        baseline_probs = self.diagnose(symptoms, return_all_probabilities=True)
        baseline_confidence = baseline_probs.get(expected_disease, 0)
        
        print(f"Baseline confidence: {baseline_confidence:.2%}")
        
        # Test removing each symptom
        removal_impact = {}
        for i, symptom in enumerate(symptoms):
            remaining = [s for j, s in enumerate(symptoms) if j != i]
            if not remaining:  # Don't test empty symptom list
                continue
                
            result_probs = self.diagnose(remaining, return_all_probabilities=True)
            new_confidence = result_probs.get(expected_disease, 0)
            impact = baseline_confidence - new_confidence
            
            removal_impact[symptom] = {
                'confidence_without': new_confidence,
                'impact': impact
            }
            
            print(f"Without '{symptom}': {new_confidence:.2%} (Impact: {impact:.2%})")
        
        # Sort symptoms by impact
        sorted_by_impact = sorted(
            removal_impact.items(), 
            key=lambda x: abs(x[1]['impact']), 
            reverse=True
        )
        
        most_important = [item[0] for item in sorted_by_impact[:3]]
        print(f"\nMost important symptoms: {', '.join(most_important)}")
        
        return {
            'disease': expected_disease,
            'baseline_symptoms': symptoms,
            'baseline_confidence': baseline_confidence,
            'symptom_importance': removal_impact,
            'most_important': most_important
        }
    
    def generate_edge_cases(self, num_cases=10):
        """Generate edge cases with mixed symptoms from different diseases
        
        Args:
            num_cases: Number of edge cases to generate
            
        Returns:
            List of test cases
        """
        # Get standard test cases organized by disease
        standard_cases = get_standard_test_cases()
        disease_symptoms = {}
        
        for case in standard_cases:
            disease = case['expected']
            if disease not in disease_symptoms:
                disease_symptoms[disease] = []
            
            disease_symptoms[disease].extend(case['symptoms'])
            
            # Remove duplicates
            disease_symptoms[disease] = list(set(disease_symptoms[disease]))
        
        # Generate edge cases by mixing symptoms
        edge_cases = []
        diseases = list(disease_symptoms.keys())
        
        for i in range(num_cases):
            # Select 2-3 random diseases to mix
            num_diseases = random.randint(2, min(3, len(diseases)))
            selected_diseases = random.sample(diseases, num_diseases)
            
            # Primary disease (the expected one)
            primary_disease = selected_diseases[0]
            
            # Mix symptoms
            mixed_symptoms = []
            
            # Add 2-3 symptoms from primary disease
            primary_symptom_count = random.randint(2, min(3, len(disease_symptoms[primary_disease])))
            mixed_symptoms.extend(random.sample(disease_symptoms[primary_disease], primary_symptom_count))
            
            # Add 1-2 symptoms from each other disease
            for disease in selected_diseases[1:]:
                symptom_count = random.randint(1, min(2, len(disease_symptoms[disease])))
                mixed_symptoms.extend(random.sample(disease_symptoms[disease], symptom_count))
            
            # Create edge case
            edge_case = {
                'category': 'Edge Case',
                'symptoms': mixed_symptoms,
                'expected': primary_disease,
                'mixed_with': selected_diseases[1:]
            }
            
            edge_cases.append(edge_case)
        
        return edge_cases

def get_standard_test_cases():
    """Return a comprehensive set of standard test cases"""
    return [
        # Original test cases
        {
            "category": "Respiratory",
            "symptoms": ["coughing", "difficulty breathing", "nasal discharge"],
            "expected": "Bovine Respiratory Disease"
        },
        {
            "category": "Skin Conditions",
            "symptoms": ["hair loss", "crusty patches", "circular lesions"],
            "expected": "Ringworm"
        },
        {
            "category": "Udder Health",
            "symptoms": ["swollen udder", "decreased milk production", "heat in udder"],
            "expected": "Mastitis"
        },
        {
            "category": "Systemic Diseases",
            "symptoms": ["fever", "weakness", "anemia", "jaundice"],
            "expected": "Anaplasmosis"
        },
        {
            "category": "Nervous System",
            "symptoms": ["lockjaw", "muscle stiffness", "hypersensitivity"],
            "expected": "Tetanus"
        },
        
        # Additional standard test cases
        {
            "category": "Digestive",
            "symptoms": ["diarrhea", "bloody feces", "fever", "dehydration"],
            "expected": "Bovine Viral Diarrhea"
        },
        {
            "category": "Foot Health",
            "symptoms": ["lameness", "swelling between hooves", "foul odor", "lesions"],
            "expected": "Foot Rot"
        },
        {
            "category": "Reproductive",
            "symptoms": ["abortion", "retained placenta", "vaginal discharge", "fever"],
            "expected": "Brucellosis"
        },
        {
            "category": "Digestive",
            "symptoms": ["bloating", "abdominal distension", "discomfort", "reduced feed intake"],
            "expected": "Bloat"
        },
        {
            "category": "Eye Conditions",
            "symptoms": ["excessive tearing", "squinting", "cloudy cornea", "redness"],
            "expected": "Pinkeye"
        },
        {
            "category": "Digestive",
            "symptoms": ["chronic weight loss", "diarrhea", "normal appetite", "bottle jaw"],
            "expected": "Johne's Disease"
        },
        {
            "category": "Musculoskeletal",
            "symptoms": ["sudden lameness", "hot swelling in muscles", "crackling under skin", "fever"],
            "expected": "Blackleg"
        },
        {
            "category": "Respiratory/Oral",
            "symptoms": ["excessive drooling", "lesions on tongue", "lesions on feet", "fever"],
            "expected": "Foot and Mouth Disease"
        }
    ]

def run_comprehensive_testing():
    """Run comprehensive testing with standard and edge cases"""
    # Initialize tester
    tester = ModelTester()
    
    # Get standard test cases
    standard_cases = get_standard_test_cases()
    
    # Run standard tests
    print("\n🔖 RUNNING STANDARD TEST CASES")
    print("============================")
    standard_results = tester.run_test_suite(standard_cases)
    
    # Generate and run edge cases
    print("\n🔖 GENERATING AND RUNNING EDGE CASES")
    print("=================================")
    edge_cases = tester.generate_edge_cases(num_cases=7)
    for i, case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}:")
        print(f"Primary disease: {case['expected']}")
        print(f"Mixed with: {', '.join(case['mixed_with'])}")
        print(f"Mixed symptoms: {', '.join(case['symptoms'])}")
    
    edge_results = tester.run_test_suite(edge_cases)
    
    # Generate symptom impact analysis for a few key diseases
    print("\n🔖 SYMPTOM IMPACT ANALYSIS")
    print("=======================")
    # Find a few cases that were diagnosed correctly
    passed_cases = [case for case, result in zip(standard_cases, standard_results['detailed_results']) 
                   if result['passed']]
    
    # Select up to 3 cases for detailed analysis
    analysis_cases = passed_cases[:3] if len(passed_cases) >= 3 else passed_cases
    
    for case in analysis_cases:
        tester.analyze_symptom_impact(
            case['symptoms'],
            case['expected']
        )
        print("\n")
    
    # Generate comprehensive report
    print("\n🔖 GENERATING COMPREHENSIVE REPORT")
    print("===============================")
    tester.generate_report()

def main():
    """Main function with options for different testing approaches"""
    # Basic test - original functionality
    test_cases = get_standard_test_cases()[:5]  # Use only the original 5 for basic test
    
    print("🐄 Testing Cattle Disease Diagnosis Model")
    print("=======================================")

    tester = ModelTester()
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['category']}")
        print(f"Symptoms: {', '.join(test_case['symptoms'])}")
        print(f"Expected: {test_case['expected']}")
        
        results = tester.test_diagnosis(test_case['symptoms'])
        
        if results and results[0]['disease'] == test_case['expected']:
            success_count += 1
            print("✅ Test Passed")
        else:
            print("❌ Test Failed")
    
    # Print summary
    print("\n📊 Test Summary")
    print(f"Passed: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")
    
    # Uncomment the line below to run comprehensive testing
    # run_comprehensive_testing()

if __name__ == "__main__":
    main()