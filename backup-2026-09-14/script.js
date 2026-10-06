(() => {
  'use strict';

  const config = window.JARVISH_CONFIG || { site: {}, plans: {} };
  const track = (event, detail = {}) => {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, ...detail });
    document.dispatchEvent(new CustomEvent('jarvish:analytics', { detail: { event, ...detail } }));
  };

  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#site-nav');
  navToggle?.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
  nav?.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      nav.classList.remove('open');
      navToggle?.setAttribute('aria-expanded', 'false');
    }
  });

  document.querySelectorAll('[data-event]').forEach((link) => {
    link.addEventListener('click', () => track('cta_click', { cta: link.dataset.event }));
  });

  const revealObserver = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries, observer) => entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      }), { threshold: 0.08 })
    : null;
  document.querySelectorAll('.reveal').forEach((item) => {
    if (revealObserver) revealObserver.observe(item);
    else item.classList.add('visible');
  });

  const filters = document.querySelectorAll('[data-filter]');
  const capabilityCards = document.querySelectorAll('.cap-card');
  filters.forEach((button) => button.addEventListener('click', () => {
    filters.forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const value = button.dataset.filter;
    capabilityCards.forEach((card) => { card.hidden = value !== 'all' && card.dataset.status !== value; });
    track('capability_filter', { status: value });
  }));

  const pricingButtons = document.querySelectorAll('[data-pricing]');
  const personalPrices = document.querySelector('.personal-prices');
  const officePrices = document.querySelector('.office-prices');
  pricingButtons.forEach((button) => button.addEventListener('click', () => {
    pricingButtons.forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const showOffice = button.dataset.pricing === 'office';
    if (personalPrices) personalPrices.hidden = showOffice;
    if (officePrices) officePrices.hidden = !showOffice;
    track('pricing_view', { category: button.dataset.pricing });
  }));

  const endpoint = String(config.site?.leadEndpoint || '').trim();
  async function submitLead(form, status) {
    status.classList.remove('error');
    if (!form.checkValidity()) {
      status.textContent = 'Please complete the required fields and consent checkbox.';
      status.classList.add('error');
      form.reportValidity();
      return;
    }
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    payload.submittedAt = new Date().toISOString();
    payload.source = document.body.dataset.page || 'website';
    track('lead_form_complete', { useType: payload.useType, framework: payload.framework, capability: payload.capability, plan: payload.plan });
    if (!endpoint) {
      status.textContent = 'Saved locally for this demo only — nothing was transmitted. Connect the private form endpoint to accept submissions.';
      form.dataset.state = 'local-demo';
      return;
    }
    status.textContent = 'Sending securely…';
    try {
      const response = await fetch(endpoint, {
        method: config.site?.leadEndpointMethod || 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      form.reset();
      status.textContent = 'Thanks — your request was received privately. We’ll be in touch.';
      form.dataset.state = 'submitted';
    } catch (error) {
      status.textContent = 'We couldn’t submit that safely. Nothing was stored here; please try again later.';
      status.classList.add('error');
      track('lead_form_error', { message: error.message });
    }
  }

  document.querySelectorAll('[data-lead-form]').forEach((form) => {
    const status = form.querySelector('.form-status');
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      submitLead(form, status);
    });
  });

  const checkout = document.querySelector('[data-checkout]');
  if (checkout) {
    const planInputs = checkout.querySelectorAll('input[name="plan"]');
    const selectedName = checkout.querySelector('[data-selected-plan]');
    const selectedPrice = checkout.querySelector('[data-selected-price]');
    const interestPlan = checkout.querySelector('input[name="selectedPlan"]');
    const updatePlan = () => {
      const chosen = checkout.querySelector('input[name="plan"]:checked');
      const plan = config.plans?.[chosen?.value] || config.plans?.connect;
      if (!plan) return;
      selectedName.textContent = plan.name;
      selectedPrice.textContent = `${plan.price} ${plan.cadence}`;
      if (interestPlan) interestPlan.value = plan.id;
      checkout.dataset.plan = plan.id;
      track('plan_selected', { plan: plan.id });
    };
    planInputs.forEach((input) => input.addEventListener('change', updatePlan));
    const requested = new URLSearchParams(location.search).get('plan');
    const requestedInput = checkout.querySelector(`input[name="plan"][value="${CSS.escape(requested || '')}"]`);
    if (requestedInput) requestedInput.checked = true;
    updatePlan();
    checkout.querySelector('[data-checkout-button]')?.addEventListener('click', () => {
      const chosen = checkout.querySelector('input[name="plan"]:checked')?.value;
      const notice = checkout.querySelector('.checkout-status');
      notice.textContent = 'Secure checkout is not active yet. No card details were requested or collected. Submit your interest below and we’ll notify you when checkout is connected.';
      document.querySelector('#plan-interest')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      track('checkout_placeholder', { plan: chosen });
    });
  }
})();
