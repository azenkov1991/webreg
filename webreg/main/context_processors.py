from .models import Patient


def patient(request):
    "A context processor that provides patient"
    patient_id = request.session.get('patient_id', None)
    if not patient_id:
        patient = None
    else:
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            patient = None
    return {
        'patient': patient,
    }
