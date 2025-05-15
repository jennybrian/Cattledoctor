from django.db import models
from django.conf import settings
from django.utils import timezone

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
    confidence_score = models.FloatField()

    def __str__(self):
        return f"Diagnosis for {self.disease.name} (Confidence: {self.confidence_score}%)"

class DiagnosisHistory(models.Model):  # ✅ Defined separately
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptoms = models.ManyToManyField(Symptom)
    diagnosis_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Diagnosis histories"
        ordering = ['-diagnosis_date']

    def __str__(self):
        return f"{self.disease.name} - {self.diagnosis_date.strftime('%Y-%m-%d')}"
