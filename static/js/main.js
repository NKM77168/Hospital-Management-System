/**
 * Hospital Management System — main.js
 * Client-side form validation, UX enhancements, and interactivity
 */

/* ═══════════════════════════════════════════════
   DATE / TIME DISPLAY
   ═══════════════════════════════════════════════ */
function updateDateTime() {
  const el = document.getElementById('datetime-display');
  if (!el) return;
  const now = new Date();
  const opts = {
    weekday: 'short', year: 'numeric', month: 'short',
    day: 'numeric', hour: '2-digit', minute: '2-digit'
  };
  el.textContent = now.toLocaleDateString('en-IN', opts);
}
updateDateTime();
setInterval(updateDateTime, 60000);

/* ═══════════════════════════════════════════════
   SET TODAY AS DEFAULT DATE IN DATE INPUTS
   ═══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"]:not([value])').forEach(input => {
    if (!input.value) input.value = today;
  });
});

/* ═══════════════════════════════════════════════
   FLASH MESSAGE AUTO-DISMISS (after 4 seconds)
   ═══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.flash-alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .5s ease, transform .5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
});

/* ═══════════════════════════════════════════════
   FORM VALIDATION — Patient Form
   ═══════════════════════════════════════════════ */
function validatePatientForm(form) {
  let valid = true;
  clearErrors(form);

  const name  = form.querySelector('#name');
  const age   = form.querySelector('#age');
  const phone = form.querySelector('#phone');
  const email = form.querySelector('#email');

  if (!name.value.trim() || name.value.trim().length < 2) {
    showError(name, 'Patient name must be at least 2 characters.');
    valid = false;
  }

  if (!age.value || parseInt(age.value) < 1 || parseInt(age.value) > 150) {
    showError(age, 'Age must be between 1 and 150.');
    valid = false;
  }

  if (!phone.value.trim() || !/^\d{10,15}$/.test(phone.value.trim())) {
    showError(phone, 'Phone number must be 10–15 digits.');
    valid = false;
  }

  if (email.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    showError(email, 'Please enter a valid email address.');
    valid = false;
  }

  return valid;
}

/* ═══════════════════════════════════════════════
   FORM VALIDATION — Appointment Form
   ═══════════════════════════════════════════════ */
function validateAppointmentForm(form) {
  let valid = true;
  clearErrors(form);

  const patientId  = form.querySelector('#patient_id');
  const doctor     = form.querySelector('#doctor');
  const department = form.querySelector('#department');
  const date       = form.querySelector('#date');
  const time       = form.querySelector('#time');

  if (!patientId.value) {
    showError(patientId, 'Please select a patient.');
    valid = false;
  }
  if (!doctor.value.trim()) {
    showError(doctor, 'Doctor name is required.');
    valid = false;
  }
  if (!department.value.trim()) {
    showError(department, 'Department is required.');
    valid = false;
  }
  if (!date.value) {
    showError(date, 'Appointment date is required.');
    valid = false;
  }
  if (!time.value) {
    showError(time, 'Appointment time is required.');
    valid = false;
  }

  return valid;
}

/* ═══════════════════════════════════════════════
   FORM VALIDATION — Billing Form
   ═══════════════════════════════════════════════ */
function validateBillForm(form) {
  let valid = true;
  clearErrors(form);

  const patientId = form.querySelector('#patient_id');
  const amount    = form.querySelector('#amount');
  const date      = form.querySelector('#date');

  if (!patientId.value) {
    showError(patientId, 'Please select a patient.');
    valid = false;
  }

  const services = form.querySelectorAll('input[name="services"]:checked');
  if (services.length === 0) {
    const servicesGroup = form.querySelector('.services-group');
    if (servicesGroup) {
      const errEl = document.createElement('div');
      errEl.className = 'field-error';
      errEl.textContent = 'Please select at least one service.';
      servicesGroup.appendChild(errEl);
    }
    valid = false;
  }

  if (!amount.value || parseFloat(amount.value) <= 0) {
    showError(amount, 'Amount must be greater than 0.');
    valid = false;
  }

  if (!date.value) {
    showError(date, 'Billing date is required.');
    valid = false;
  }

  return valid;
}

/* ═══════════════════════════════════════════════
   ERROR HELPERS
   ═══════════════════════════════════════════════ */
function showError(input, message) {
  input.classList.add('is-invalid');
  const err = document.createElement('div');
  err.className = 'field-error';
  err.style.cssText = 'color:#ef476f;font-size:.78rem;margin-top:.3rem;';
  err.textContent = message;
  if (input.parentElement) {
    input.parentElement.appendChild(err);
  }
}

function clearErrors(form) {
  form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  form.querySelectorAll('.field-error').forEach(el => el.remove());
}

/* ═══════════════════════════════════════════════
   DELETE CONFIRMATION MODAL
   ═══════════════════════════════════════════════ */
function confirmDelete(formId, itemName) {
  const message = `Are you sure you want to delete "${itemName}"?\nThis action cannot be undone.`;
  if (window.confirm(message)) {
    document.getElementById(formId).submit();
  }
}

/* ═══════════════════════════════════════════════
   AMOUNT AUTO-CALCULATE (Billing)
   ═══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
  const serviceCheckboxes = document.querySelectorAll('.service-checkbox');
  const amountInput = document.getElementById('amount');

  if (serviceCheckboxes.length && amountInput && !amountInput.dataset.manual) {
    const servicePrices = {
      'Consultation': 500, 'Lab Test': 800, 'X-Ray': 600, 'MRI Scan': 4500,
      'CT Scan': 3500, 'Blood Test': 400, 'Urine Test': 300, 'ECG': 700,
      'Ultrasound': 1200, 'Physiotherapy': 900, 'Surgery': 15000,
      'ICU Charges': 5000, 'Room Charges': 2000, 'Medication': 600, 'Nursing': 1000,
    };

    function recalcAmount() {
      let total = 0;
      serviceCheckboxes.forEach(cb => {
        if (cb.checked) {
          total += servicePrices[cb.value] || 0;
        }
      });
      amountInput.value = total;
    }

    serviceCheckboxes.forEach(cb => cb.addEventListener('change', recalcAmount));

    // Mark as manual edit if user types
    amountInput.addEventListener('input', () => {
      amountInput.dataset.manual = 'true';
    });
  }
});

/* ═══════════════════════════════════════════════
   SIDEBAR TOGGLE (Mobile)
   ═══════════════════════════════════════════════ */
function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

/* ═══════════════════════════════════════════════
   TABLE ROW CLICK — navigate to detail page
   ═══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function (e) {
      // Don't navigate if clicking on action buttons
      if (e.target.closest('.btn-icon, button, a, form')) return;
      window.location.href = this.dataset.href;
    });
  });
});

/* ═══════════════════════════════════════════════
   PRINT INVOICE
   ═══════════════════════════════════════════════ */
function printInvoice() {
  window.print();
}

/* ═══════════════════════════════════════════════
   ATTACH FORM VALIDATORS ON SUBMIT
   ═══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
  const patientForm = document.getElementById('patient-form');
  if (patientForm) {
    patientForm.addEventListener('submit', function (e) {
      if (!validatePatientForm(this)) e.preventDefault();
    });
  }

  const apptForm = document.getElementById('appointment-form');
  if (apptForm) {
    apptForm.addEventListener('submit', function (e) {
      if (!validateAppointmentForm(this)) e.preventDefault();
    });
  }

  const billForm = document.getElementById('bill-form');
  if (billForm) {
    billForm.addEventListener('submit', function (e) {
      if (!validateBillForm(this)) e.preventDefault();
    });
  }
});
