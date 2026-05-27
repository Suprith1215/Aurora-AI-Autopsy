import { NextResponse } from "next/server";
import { state } from "../state";

export async function GET() {
  // Synthesize metrics from current logs and incidents
  const totalIncidents = state.incidents.length;
  const promptInjections = state.blockedPayloads.length;
  const hallucinations = state.incidents.filter(i => i.failure_type.toLowerCase() === "hallucination").length;
  const driftEvents = state.incidents.filter(i => i.failure_type.toLowerCase() === "data drift").length;

  const metrics = {
    incident_count: totalIncidents,
    active_threats: promptInjections,
    avg_remediation_ms: 1280,
    network_health: "Healthy",
    drift_score: 0.04,
    failure_distribution: {
      hallucinations,
      prompt_injections: promptInjections,
      drift_events: driftEvents
    }
  };

  return NextResponse.json({
    reliability_score: state.reliabilityScore,
    metrics,
    incidents: state.incidents
  });
}
