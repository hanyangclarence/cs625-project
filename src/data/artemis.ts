import type { Topic } from '../types/news'

export const artemis: Topic = {
  id: 'artemis-ii-lunar-flyby',
  title: 'Artemis II lunar flyby',
  sources: [
    {
      id: 'nasa',
      outlet: 'NASA',
      date: '2026-04-04',
      articleTitle: 'Artemis II completes lunar flyby, sets distance record from Earth',
      imageUrl:
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=60',
      matchTag: 'shared-facts',
      matchScore: 97,
      trustScore: 88,
      trustLabel: 'High',
      summary: 'Primary source. Direct agency release with full mission log references.',
      rubric: { references: 30, authority: 30, clarity: 28 },
    },
    {
      id: 'ap',
      outlet: 'AP News',
      date: '2026-04-05',
      articleTitle: 'NASA says Artemis II crew completed lunar flyby overnight',
      imageUrl:
        'https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?auto=format&fit=crop&w=800&q=60',
      matchTag: 'shared-facts',
      matchScore: 94,
      trustScore: 82,
      trustLabel: 'High',
      summary:
        'Well-supported wire report. Attributes claims to NASA, minimal interpretation added.',
      rubric: { references: 28, authority: 28, clarity: 26 },
    },
    {
      id: 'guardian',
      outlet: 'The Guardian',
      date: '2026-04-06',
      articleTitle: 'Artemis II: what the lunar flyby means for the return-to-Moon timeline',
      imageUrl:
        'https://images.unsplash.com/photo-1454789548928-9efd52dc4031?auto=format&fit=crop&w=800&q=60',
      matchTag: 'framing-gaps',
      matchScore: 71,
      trustScore: 56,
      trustLabel: 'Medium',
      summary:
        'Supports the event, but reframes it around political timeline rather than mission facts.',
      rubric: { references: 22, authority: 20, clarity: 14 },
    },
    {
      id: 'npr',
      outlet: 'NPR',
      date: '2026-04-18',
      articleTitle: "Weeks after Artemis II's flyby, questions about reusability",
      imageUrl:
        'https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=800&q=60',
      matchTag: 'evidence-support',
      matchScore: 83,
      trustScore: 74,
      trustLabel: 'High',
      summary: 'Later follow-up. Cites NASA technical briefing and independent engineers.',
      rubric: { references: 28, authority: 26, clarity: 20 },
    },
  ],
  claims: [
    {
      id: 'c-flyby',
      text: 'Artemis II completed its crewed lunar flyby and set a new crewed-distance record from Earth.',
      overallTrust: 'High',
      evidence: [
        {
          sourceId: 'nasa',
          passage:
            'At 02:14 UTC, Orion executed the outbound powered flyby burn, passing approximately 7,400 km above the lunar far side — the furthest any crewed vehicle has travelled from Earth.',
          supportLevel: 'strong',
          score: 96,
        },
        {
          sourceId: 'ap',
          passage:
            'NASA said the four-person Artemis II crew completed a lunar flyby overnight, reaching a record distance from Earth of roughly 400,000 km.',
          supportLevel: 'strong',
          score: 91,
        },
        {
          sourceId: 'guardian',
          passage:
            'The flyby, confirmed by NASA, is presented domestically as a prelude to a 2027 landing attempt.',
          supportLevel: 'partial',
          score: 68,
        },
      ],
    },
    {
      id: 'c-crew',
      text: 'The Artemis II crew consists of four astronauts, including one Canadian Space Agency mission specialist.',
      overallTrust: 'High',
      evidence: [
        {
          sourceId: 'nasa',
          passage:
            'Commander Reid Wiseman, Pilot Victor Glover, Mission Specialist Christina Koch, and CSA Mission Specialist Jeremy Hansen comprise the Artemis II crew.',
          supportLevel: 'strong',
          score: 98,
        },
        {
          sourceId: 'ap',
          passage: 'The four-person crew includes a Canadian astronaut, NASA confirmed.',
          supportLevel: 'strong',
          score: 88,
        },
      ],
    },
    {
      id: 'c-distance',
      text: 'The mission reached roughly 400,000 km from Earth, the furthest a crewed vehicle has travelled.',
      overallTrust: 'Medium',
      evidence: [
        {
          sourceId: 'nasa',
          passage:
            'Peak range from Earth center: 401,250 km — exceeding the previous crewed record set by Apollo 13 in 1970.',
          supportLevel: 'strong',
          score: 95,
        },
        {
          sourceId: 'guardian',
          passage:
            'Reports describe the mission as the furthest-crewed mission in history, though precise figures vary between briefings.',
          supportLevel: 'partial',
          score: 58,
        },
        {
          sourceId: 'npr',
          passage:
            'Independent trackers place peak range near 401,000 km, broadly consistent with NASA figures.',
          supportLevel: 'strong',
          score: 81,
        },
      ],
    },
    {
      id: 'c-return',
      text: 'Orion is on a free-return trajectory and is scheduled to splash down in the Pacific around April 14.',
      overallTrust: 'Medium',
      evidence: [
        {
          sourceId: 'nasa',
          passage:
            'A free-return trajectory was selected to conserve propellant; splashdown is targeted for April 14, 2026 in the Pacific recovery zone.',
          supportLevel: 'strong',
          score: 92,
        },
        {
          sourceId: 'ap',
          passage: 'Recovery teams are pre-positioning for a Pacific splashdown next week.',
          supportLevel: 'partial',
          score: 64,
        },
      ],
    },
    {
      id: 'c-objectives',
      text: 'Artemis II validates Orion life-support, navigation, and deep-space communications ahead of the Artemis III landing.',
      overallTrust: 'Medium',
      evidence: [
        {
          sourceId: 'nasa',
          passage:
            'Primary objectives: evaluate ECLSS performance in cislunar space, validate optical navigation, and stress-test DSN link margins.',
          supportLevel: 'strong',
          score: 90,
        },
        {
          sourceId: 'npr',
          passage:
            'Engineers outside NASA said the flight plan also stress-tests reusability assumptions for later Artemis flights.',
          supportLevel: 'partial',
          score: 62,
        },
        {
          sourceId: 'guardian',
          passage:
            'Commentary frames the flight as political signalling rather than a narrow engineering rehearsal.',
          supportLevel: 'weaker',
          score: 34,
        },
      ],
    },
  ],
  timeline: [
    {
      id: 't1',
      date: '2026-04-04',
      sourceId: 'nasa',
      stage: 'Appears',
      shortNote: 'First NASA release — flight data and mission log published.',
      claimId: 'c-flyby',
    },
    {
      id: 't2',
      date: '2026-04-05',
      sourceId: 'ap',
      stage: 'Picked up',
      shortNote: 'AP mirrors the NASA lede, attributes distance figure to the agency.',
      claimId: 'c-flyby',
    },
    {
      id: 't3',
      date: '2026-04-06',
      sourceId: 'guardian',
      stage: 'Supplemented',
      shortNote: 'Guardian adds political framing about the 2027 landing timeline.',
      claimId: 'c-objectives',
    },
    {
      id: 't4',
      date: '2026-04-08',
      sourceId: 'nasa',
      stage: 'Supplemented',
      shortNote: 'NASA posts technical briefing with peak-range number (401,250 km).',
      claimId: 'c-distance',
    },
    {
      id: 't5',
      date: '2026-04-18',
      sourceId: 'npr',
      stage: 'Supplemented',
      shortNote: 'NPR adds reusability context from independent engineers.',
      claimId: 'c-objectives',
    },
  ],
}
