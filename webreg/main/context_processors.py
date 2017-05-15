from .models import Patient


def patient(request):
    "A context processor that provides patient"
    patient_id = request.session.get('patient_id', None)
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        patient = None
    return {
        'patient': patient,
    }
