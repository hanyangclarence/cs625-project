export type MatchTag = 'shared-facts' | 'framing-gaps' | 'evidence-support'
export type TrustLabel = 'High' | 'Medium' | 'Low'
export type SupportLevel = 'strong' | 'partial' | 'weaker'
export type TimelineStage = 'Appears' | 'Picked up' | 'Supplemented'

export interface Source {
  id: string
  outlet: string
  date: string
  articleTitle: string
  imageUrl?: string
  matchTag: MatchTag
  matchScore: number
  trustScore: number
  trustLabel: TrustLabel
  summary: string
  rubric: { references: number; authority: number; clarity: number }
}

export interface EvidenceLink {
  sourceId: string
  passage: string
  supportLevel: SupportLevel
  score: number
}

export interface Claim {
  id: string
  text: string
  overallTrust: TrustLabel
  evidence: EvidenceLink[]
}

export interface TimelineEntry {
  id: string
  date: string
  sourceId: string
  stage: TimelineStage
  shortNote?: string
  claimId?: string
}

export interface Topic {
  id: string
  title: string
  sources: Source[]
  claims: Claim[]
  timeline: TimelineEntry[]
}

export function deriveTrustLabel(score: number): TrustLabel {
  if (score > 60) return 'High'
  if (score >= 30) return 'Medium'
  return 'Low'
}
