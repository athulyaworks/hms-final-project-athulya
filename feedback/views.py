from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import DoctorFeedback, HospitalFeedback
from .forms import DoctorFeedbackForm, HospitalFeedbackForm
from hospital.models import Doctor
from django.contrib import messages
from django.shortcuts import redirect

from django.urls import reverse_lazy
from django.shortcuts import redirect

class DoctorFeedbackCreateView(LoginRequiredMixin, CreateView):
    model = DoctorFeedback
    form_class = DoctorFeedbackForm
    template_name = 'feedback/doctor_feedback.html'

    def dispatch(self, request, *args, **kwargs):
        self.doctor = get_object_or_404(Doctor, id=self.kwargs['doctor_id'])
        patient = self.request.user.patient_profile
        if DoctorFeedback.objects.filter(doctor=self.doctor, patient=patient).exists():
            messages.warning(request, "You have already submitted feedback for this doctor.")
            return redirect('feedback:doctor-detail', pk=self.doctor.id)  # FIXED here
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.patient = self.request.user.patient_profile
        form.instance.doctor_id = self.kwargs['doctor_id']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctor'] = self.doctor
        return context

    def get_success_url(self):
        return reverse_lazy('feedback:doctor-detail', kwargs={'pk': self.doctor.id})  # FIXED here


from django.shortcuts import render

class HospitalFeedbackCreateView(LoginRequiredMixin, CreateView):
    model = HospitalFeedback
    form_class = HospitalFeedbackForm
    template_name = 'feedback/hospital_feedback.html'
    success_url = reverse_lazy('hospital:patient-dashboard')

    def dispatch(self, request, *args, **kwargs):
        patient = request.user.patient_profile
        existing_feedback = HospitalFeedback.objects.filter(patient=patient).first()
        if existing_feedback:
            # Render a template showing that feedback is already submitted
            return render(request, 'feedback/hospital_feedback_already_submitted.html', {
                'feedback': existing_feedback
            })
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.patient = self.request.user.patient_profile
        return super().form_valid(form)


# views.py (add this new view for Option 2 - shared feedback among same-doctor patients)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from hospital.models import Doctor
from .models import DoctorFeedback

@login_required
def doctor_feedback_list_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = request.user.patient_profile

    # Ensure the patient had at least one appointment with this doctor
    has_seen_doctor = doctor.appointments.filter(patient=patient).exists()

    if not has_seen_doctor:
        return render(request, 'feedback/unauthorized.html', {'doctor': doctor})

    feedbacks = DoctorFeedback.objects.filter(doctor=doctor).select_related('patient')
    return render(request, 'feedback/doctor_feedback_list.html', {
        'doctor': doctor,
        'feedbacks': feedbacks
    })



from django.views.generic import DetailView
from .models import DoctorFeedback
from hospital.models import Doctor
from django.db.models import Avg

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor
    template_name = 'feedback/doctor_detail.html'
    context_object_name = 'doctor'
    pk_url_kwarg = 'pk'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feedbacks = DoctorFeedback.objects.filter(doctor=self.object)
        context['feedbacks'] = feedbacks
        avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg']
        context['avg_rating'] = avg_rating if avg_rating is not None else 0
        return context
