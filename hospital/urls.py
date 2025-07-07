from django.urls import path
from hospital.views import (
    book_appointment,
    patient_edit_view,
    appointment_list,
    appointment_list_admin,
    # manage_patient_registration,
    toggle_patient_checkin,
    patient_checkin_list,
    waiting_list_view,
    remove_waiting_list_entry,
    send_reminders,
    patient_list_view,
    patient_detail_view,
    DoctorPatientListView,
    ReceptionistPatientListView,
    PharmacistPatientListView,
    PrescriptionUploadView,
    add_daily_note,
    add_treatment,
    add_procedure,
    patient_dashboard,
    reschedule_appointment,
    cancel_appointment,
    request_admission,
    admission_requests_list,
    admit_patient,
    process_admission_request,
    assign_bed_and_admit,
    BedCreateView,
    AdminBedListView,
    AdminInpatientListView,
    ContactHTMLView,
    DoctorListHTMLView,
    PatientListHTMLView, 
    
    )

from hospital.views_api import(
    AppointmentListHTMLView,
    PublicDoctorDirectoryView,
)


from users.views import ReceptionistDashboardView

app_name = 'hospital'

urlpatterns = [
    # Appointments
    path('appointments/book/', book_appointment, name='book-appointment'),
    path('doctors-list/', DoctorListHTMLView.as_view(), name='doctors_list'),
    path('patients-list/', PatientListHTMLView.as_view(), name='patients_list'),
    path('appointments-page/', AppointmentListHTMLView.as_view(), name='appointments_page'),
    path('appointments/', appointment_list, name='appointments_list'),
    path('dashboard/admin/appointments/', appointment_list_admin, name='admin_appointments'),

    # Beds (Admin)
    path('dashboard/admin/beds/', AdminBedListView.as_view(), name='admin_beds'),
    path('beds/add/', BedCreateView.as_view(), name='add-bed'),

    # Receptionist
    path('receptionist/dashboard/', ReceptionistDashboardView.as_view(), name='receptionist-dashboard'),
    # path('receptionist/patients/register/', manage_patient_registration, name='receptionist-patient-register'),

    # Patient check-in
    path('patients/checkin/', patient_checkin_list, name='patient-checkin-list'),
    path('patients/checkin/<int:pk>/toggle/', toggle_patient_checkin, name='toggle-patient-checkin'),

    # Waiting list and reminders
    path('waiting-list/', waiting_list_view, name='waiting-list'),
    path('waiting-list/remove/<int:pk>/', remove_waiting_list_entry, name='remove-waiting-list-entry'),
    path('send-reminders/', send_reminders, name='send-reminders'),

    # Patients
    path('patients/', patient_list_view, name='patient-list'),
    path('patients/<int:pk>/', patient_detail_view, name='patient-detail'),

    # Patient Dashboard
    path('dashboard/patient/', patient_dashboard, name='patient-dashboard'),

    # Doctors directory
    path('doctors-directory/', PublicDoctorDirectoryView.as_view(), name='public_doctor_directory'),

    # Appointment management
    
    path('appointment/<int:appointment_id>/reschedule/', reschedule_appointment, name='reschedule-appointment'),
    path('appointment/<int:appointment_id>/cancel/', cancel_appointment, name='cancel-appointment'),


    # Doctor, Receptionist, Pharmacist patient lists
    path('doctor/patients/', DoctorPatientListView.as_view(), name='doctor-patient-list'),
    path('receptionist/patients/', ReceptionistPatientListView.as_view(), name='receptionist-patient-list'),
    path('pharmacist/patients/', PharmacistPatientListView.as_view(), name='pharmacist-patient-list'),

    # Prescriptions
    path('prescriptions/upload/<int:appointment_id>/', PrescriptionUploadView.as_view(), name='prescription-upload'),

    # Inpatient management
    path('inpatient/<int:pk>/add-daily-note/', add_daily_note, name='add-daily-note'),
    path('inpatient/<int:pk>/add-treatment/', add_treatment, name='add-treatment'),
    path('inpatient/<int:pk>/add-procedure/', add_procedure, name='add-procedure'),

    # Admission
    path('request-admission/<int:patient_id>/', request_admission, name='request-admission'),
    path('admission-requests/', admission_requests_list, name='admission-requests-list'),
    path('admit-patient/<int:patient_id>/', admit_patient, name='admit-patient'),
    path('admission-request/<int:request_id>/<str:action>/', process_admission_request, name='process-admission-request'),
    path('admit-and-assign/<int:patient_id>/', assign_bed_and_admit, name='assign-bed-admit'),

    # Patient edit
    path('patients/<int:pk>/edit/', patient_edit_view, name='patient-edit'),

    # Admin inpatient list (duplicate with InpatientRecordListHTMLView?)
    path('dashboard/admin/inpatients/', AdminInpatientListView.as_view(), name='admin_inpatients'),


    path('contact/', ContactHTMLView.as_view(), name='contact'),
    

] 