import logging
logger = logging.getLogger(__name__)
import os
import pandas as pd
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
import joblib
from .models import DiagnosisHistory, Disease, Symptom


# Disease_info dictionary for treatment and prevention information
DISEASE_INFO = {
    # ...existing code...
    'brucellosis': {
        'treatment': 'No treatment - affected animals must be culled. Report to authorities immediately.',
        'prevention': 'Regular vaccination. Test and slaughter positive animals. Proper disposal of aborted materials.'
    },
    'bovine respiratory disease': {
        'treatment': 'Early antibiotic treatment. Anti-inflammatory drugs. Supportive care and rest.',
        'prevention': 'Vaccination program. Good ventilation. Reduce stress. Proper housing conditions.'
    },
    'black quarter': {
        'treatment': 'Early antibiotic treatment. Surgical debridement of affected areas may be necessary.',
        'prevention': 'Regular vaccination. Good pasture management. Avoid grazing in known infected areas.'
    },
    'bloat': {
        'treatment': 'Stomach tubing. Anti-foaming agents. In severe cases, emergency rumenotomy.',
        'prevention': 'Proper grazing management. Avoid sudden feed changes. Monitor high-risk feeds.'
    },
    'anaplasmosis': {
        'treatment': 'Tetracycline antibiotics. Supportive care. Blood transfusion in severe cases.',
        'prevention': 'Tick control. Regular testing. Vaccination in endemic areas.'
    },
    'pinkeye': {
        'treatment': 'Antibiotic eye ointments/injections. Eye patches. Keep animals in shade.',
        'prevention': 'Face fly control. Dust control. Vaccination. Early treatment of affected animals.'
    },
    'bovine viral diarrhea': {
        'treatment': 'Supportive care. Fluid therapy. Antibiotics for secondary infections.',
        'prevention': 'Vaccination. Testing and removal of carrier animals. Biosecurity measures.'
    },
    "johne's disease": {
        'treatment': 'No effective treatment. Affected animals should be culled.',
        'prevention': 'Test and cull program. Proper calving area hygiene. Colostrum management.'
    },
    'theileriosis': {
        'treatment': 'Anti-parasitic drugs. Supportive care. Blood transfusion if needed.',
        'prevention': 'Tick control. Strategic dipping. Vaccination in endemic areas.'
    },
    'lumpy skin disease': {
        'treatment': 'Supportive care. Antibiotics for secondary infections. Wound management.',
        'prevention': 'Vaccination. Vector control. Quarantine of new animals.'
    }
}


# Get the BASE directory of your Django project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_model")


# Load ML models and preprocessors
try:
    # Load ML models
    model = joblib.load(os.path.join(MODEL_DIR, "cattle_disease_model.pkl"))
    vectorizer = joblib.load(os.path.join(MODEL_DIR, "description_vectorizer.pkl"))
    label_encoder = joblib.load(os.path.join(MODEL_DIR, "disease_label_encoder.pkl"))
    
    # Load and process disease dataset
    try:
        disease_data = pd.read_csv(os.path.join(MODEL_DIR, "cattle_disease_dataset.csv"))
        print("Available columns:", disease_data.columns.tolist())
        
        # Initialize disease_info with hardcoded defaults
        disease_info = DISEASE_INFO.copy()
        
        # Update with data from CSV if columns exist
        if 'Disease' in disease_data.columns:
            for _, row in disease_data.iterrows():
                disease_name = row['Disease'].lower().strip()
                treatment = row.get('Treatment', 'Treatment information not available')
                prevention = row.get('Advice', 'Prevention/Advice information not available')  # Changed from 'Prevention' to 'Advice'
                
                disease_info[disease_name] = {
                    'treatment': treatment,
                    'prevention': prevention  # This will store the Advice as prevention
                }
        
        print("Loaded diseases:", ", ".join(disease_info.keys()))
    except Exception as e:
        print(f"Warning: Could not load disease dataset, using default data. Error: {str(e)}")
        disease_info = DISEASE_INFO.copy()
        
except Exception as e:
    print(f"Error loading ML models: {str(e)}")
    print(f"Looking in: {MODEL_DIR}")
    raise

# Add this function after the model loading section
def preprocess_symptoms(symptoms):
    """Preprocess symptoms to match vectorizer features"""
    symptom_mapping = {
        # Respiratory
        'breathing_difficulty': 'difficulty breathing',
        'labored_breathing': 'labored breathing',
        'rapid_breathing': 'rapid breathing',
        'nasal_discharge': 'nasal discharge',
        
        # General Condition
        'loss_of_appetite': 'decreased appetite',
        'reduced_feed_intake': 'decreased feed intake',
        'sudden_collapse': 'collapse sudden',
        'high_temperature': 'high fever',
        'weight_loss': 'loss weight',
        
        # Udder and Reproduction
        'decreased_milk_production': 'reduced milk production',
        'swollen_udder': 'swollen udder',
        'heat_in_udder': 'heat udder',
        'retained_placenta': 'retained placenta',
        
        # Digestive and Abdominal
        'excessive_salivation': 'excessive salivation',
        'watery_diarrhea': 'watery diarrhea',
        'distended_abdomen': 'distended abdomen',
        'kicking_at_stomach': 'kicking stomach',
        
        # Skin and Hair
        'circular_lesions': 'circular lesions',
        'hair_loss': 'loss hair',
        'skin_nodules': 'skin nodules',
        'crusty_patches': 'crusty patches',
        'lumpy_skin': 'lumpy skin',
        
        # Eyes and Head
        'corneal_ulceration': 'corneal ulceration',
        'eye_tearing': 'tearing eye',
        'hypersensitivity_to_stimuli': 'hypersensitivity stimuli',
        
        # Musculoskeletal
        'swollen_joints': 'swollen joints',
        'muscle_stiffness': 'muscle stiffness',
        'inability_to_stand': 'inability stand',
        'loss_of_balance': 'loss balance',
        'swollen_lymph_nodes': 'swollen lymph nodes',
        
        # Additional Important Mappings
        'lockjaw': 'lockjaw',
        'oral_lesions': 'oral lesions',
        'lameness': 'lameness',
        'cold_ears': 'cold ears',
        'jaundice': 'jaundice',
        'anemia': 'anemia',
        'dehydration': 'dehydration'
    }
    
    processed_symptoms = []
    for symptom in symptoms:
        if symptom in symptom_mapping:
            processed_symptoms.append(symptom_mapping[symptom])
        else:
            # Convert snake_case to space-separated words
            processed_symptom = symptom.replace('_', ' ').lower()
            processed_symptoms.append(processed_symptom)
    
    return processed_symptoms

@login_required
def diagnosis_history(request):
    """View for displaying user's diagnosis history"""
    histories = DiagnosisHistory.objects.filter(user=request.user).select_related('disease').prefetch_related('symptoms')
    return render(request, "diagnosis/history.html", {'histories': histories})

@login_required
def home(request):
    """Home page view requiring authentication"""
    return render(request, "home.html")

@login_required
def diagnosis_home(request):
    """Diagnosis page view requiring authentication"""
    return render(request, "diagnosis/index.html")

# Modify the predict_disease view
@login_required
@api_view(["POST"])
def predict_disease(request):
    try:
        symptoms = request.data.get("symptoms", [])
        
        if not symptoms:
            return Response({"error": "No symptoms provided"}, status=400)

        # Preprocess symptoms
        processed_symptoms = preprocess_symptoms(symptoms)
        symptoms_text = ", ".join(sorted(processed_symptoms))

        X = vectorizer.transform([symptoms_text])
        probabilities = model.predict_proba(X)[0]

        # Get top prediction above 10% threshold
        top_index = probabilities.argsort()[-1]
        top_probability = probabilities[top_index]

        if top_probability < 0.1:
            return Response({
                "predictions": [],
                "message": "No diseases matched with sufficient confidence"
            })

        predicted_disease_name = label_encoder.inverse_transform([top_index])[0].strip().lower()

        # Get disease object from DB (case-insensitive match)
        try:
            disease_obj = Disease.objects.get(name__iexact=predicted_disease_name)
        except Disease.DoesNotExist:
            disease_obj = None

        # Log diagnosis history
        if disease_obj:
            history = DiagnosisHistory.objects.create(
                user=request.user,
                disease=disease_obj,
            )
            # Add matched symptoms
            for symptom_text in processed_symptoms:
                symptom_obj, _ = Symptom.objects.get_or_create(name=symptom_text)
                history.symptoms.add(symptom_obj)

        # Return details to user
        response_data = {
            "predictions": [{
                "disease": predicted_disease_name.title(),
                "matched_symptoms": processed_symptoms,
                "treatment": disease_info.get(predicted_disease_name, {}).get("treatment", "Not available"),
                "advice": disease_info.get(predicted_disease_name, {}).get("prevention", "Not available"),
            }],
            "input_symptoms": symptoms
        }

        return Response(response_data)

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return Response({
            "error": f"Prediction failed: {str(e)}",
            "symptoms": symptoms if 'symptoms' in locals() else None
        }, status=500)