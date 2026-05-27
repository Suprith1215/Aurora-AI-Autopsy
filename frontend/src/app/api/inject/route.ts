import { NextResponse } from "next/server";
import { state } from "../state";

export async function POST(req: Request) {
  try {
    const data = await req.json();
    const desc = data.description || "Unspecified anomaly injected.";
    const model = data.model || "AURORA-NEURAL-PRO";
    const incidentId = `incid_${Date.now()}_inj`;
    
    // Determine failure class and details
    let failureType = "System Anomaly";
    let recommendedFix = "Run standard node verification.";
    let remediationPatch = "VERIFY NODE PORTAL --STATUS";
    let severity = 3;
    
    const lowerDesc = desc.toLowerCase();
    if (lowerDesc.includes("prescription") || lowerDesc.includes("cure") || lowerDesc.includes("hallucination") || lowerDesc.includes("definitely cure")) {
      failureType = "Hallucination";
      severity = 5;
      recommendedFix = "Add strict temperature constraints and boundary semantic limitations.";
      remediationPatch = "SYSTEM PROMPT PATCH:\nAdd system-level constraint: 'If the retrieved context does not contain the answer, reply \"I do not know the answer based on the provided documents.\" Do not synthesize info.'";
    } else if (lowerDesc.includes("jailbreak") || lowerDesc.includes("sudo") || lowerDesc.includes("injection") || lowerDesc.includes("ignore")) {
      failureType = "Prompt Injection";
      severity = 5;
      recommendedFix = "Instantly drop connection and log to governance ledger.";
      remediationPatch = "SECURITY LOCK COMMAND:\nDROP CONNECTION AND BLOCK IP FOR 3600s";
    } else if (lowerDesc.includes("drift") || lowerDesc.includes("threshold") || lowerDesc.includes("cosine")) {
      failureType = "Data Drift";
      severity = 4;
      recommendedFix = "Trigger automatic re-indexing job with boundary optimization.";
      remediationPatch = "AUTO REBUILD COMMAND:\npython -m aurora.data_layer.vector_store --rebuild --threshold 0.85";
    }

    const newIncident = {
      incident_id: incidentId,
      failure_type: failureType,
      severity_score: severity,
      confidence: 0.9 + Math.random() * 0.09,
      description: desc,
      recommended_fix: recommendedFix,
      remediation_patch: remediationPatch,
      remediation_status: "AUTO_DEPLOYED",
      timestamp: Date.now(),
      compliance_status: "COMPLIANT",
      model
    };

    // Update in-memory state
    state.incidents.push(newIncident);
    state.reliabilityScore = Math.max(70, state.reliabilityScore - severity * 2.5);

    // Append to event broker history
    state.historyLogs.push({
      topic: "failures",
      incident_id: incidentId,
      description: desc,
      broker_timestamp: Date.now(),
      failure_type: failureType,
      severity_score: severity,
      remediation_status: "AUTO_DEPLOYED",
      agent_trace: [
        { agent: "ObserverAgent", latency_ms: 12 + Math.floor(Math.random() * 10), timestamp: Date.now() },
        { agent: "AutopsyAgent", latency_ms: 30 + Math.floor(Math.random() * 20), timestamp: Date.now() },
        { agent: "RetrievalAgent", latency_ms: 15 + Math.floor(Math.random() * 10), timestamp: Date.now() },
        { agent: "RepairAgent", latency_ms: 50 + Math.floor(Math.random() * 40), timestamp: Date.now() },
        { agent: "ValidationAgent", latency_ms: 20 + Math.floor(Math.random() * 15), timestamp: Date.now() },
        { agent: "GovernanceAgent", latency_ms: 8 + Math.floor(Math.random() * 5), timestamp: Date.now() }
      ]
    });

    return NextResponse.json({
      success: true,
      result: newIncident
    });
  } catch (e: any) {
    return NextResponse.json({ success: false, error: e.message }, { status: 500 });
  }
}
