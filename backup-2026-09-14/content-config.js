window.JARVISH_CONFIG = Object.freeze({
  site: {
    name: 'Jarv-ish',
    baseUrl: 'https://jarv-ish.com',
    slogan: 'A little like JARVIS. A lot helpful.',
    leadEndpoint: '',
    leadEndpointMethod: 'POST'
  },
  plans: {
    connect: {
      id: 'connect',
      name: 'Jarv-ish Connect',
      price: '$49',
      cadence: '/ month',
      label: 'Bring your own agent',
      summary: 'One paid Personal seat for people bringing OpenClaw, Hermes, or another compatible agent.'
    },
    complete: {
      id: 'complete',
      name: 'Jarv-ish Complete',
      price: '$99',
      cadence: '/ month',
      label: 'Managed agent included',
      summary: 'One paid Personal seat with a hosted and configured Jarv-ish agent included.'
    }
  },
  capabilityStatuses: {
    morningBriefing: 'Available now',
    eveningRundown: 'Available now',
    meetingAttendant: 'Early access',
    whileAway: 'Early access',
    officeSwarms: 'In development',
    agentRecommendations: 'In development',
    smartDevices: 'Planned',
    smartGlasses: 'Planned'
  }
});
