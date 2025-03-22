from django.db import models

class Disease(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    treatment = models.TextField()
    advice = models.TextField()

    def __str__(self):
        return self.name

class Symptom(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Diagnosis(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptoms = models.ManyToManyField(Symptom)
    confidence_score = models.FloatField()  # ML model's prediction confidence

    def __str__(self):
        return f"Diagnosis for {self.disease.name} (Confidence: {self.confidence_score}%)"