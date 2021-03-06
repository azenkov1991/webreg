__all__= [
    'AppointmentError', 'PatientError', 'Appointment', 'Service',
    'Cabinet', 'Cell', 'Clinic', 'Department', 'NumberOfServiceRestriction','Patient',
    'ProfileSettings', 'SiteServiceRestriction', 'SlotType', 'Specialist', 'Specialization', 'UserProfile',
    'SlotRestriction', 'ServiceRestriction', 'SpecialistRestriction', 'SiteConfig'
]
from .service import *
from .appointment import *
from .cabinet import *
from .cell import *
from .clinic import *
from .department import *
from .number_of_service_restricion import *
from .patient import *
from .profile_settings import *
from .site_service_restriction import *
from .slot_type import *
from .specialist import *
from .specialization import *
from .user_profile import *
from .site_config import *


class AppointmentError(Exception):
    pass


class PatientError(Exception):
    pass




















