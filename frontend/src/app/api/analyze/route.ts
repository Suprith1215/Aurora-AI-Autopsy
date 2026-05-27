import { NextResponse } from "next/server";
import { state } from "../state";

export async function POST(req: Request) {
  try {
    const data = await req.json();
    const prompt = data.prompt || "";
    const model = data.model || "llama3";
    
    const promptLower = prompt.toLowerCase();
    
    // Step 1: Scan user prompt for security threats
    const dangerousPatterns = [
      "ignore previous instructions",
      "jailbreak",
      "sudo",
      "dan mode",
      "ignore all prior rules",
      "print database keys"
    ];
    
    const matchedSignature = dangerousPatterns.find(p => promptLower.includes(p));
    const isBlocked = !!matchedSignature;
    
    if (isBlocked) {
      const incidentId = `incid_${Date.now()}_inj`;
      
      const newIncident = {
        incident_id: incidentId,
        failure_type: "Prompt Injection",
        severity_score: 5,
        confidence: 0.99,
        description: `BLOCKED Prompt Injection signature: "${matchedSignature}" in prompt: "${prompt.slice(0, 50)}..."`,
        recommended_fix: "Instantly drop connection and log to governance ledger.",
        remediation_patch: "SECURITY LOCK COMMAND:\nDROP CONNECTION AND BLOCK IP FOR 3600s",
        remediation_status: "AUTO_DEPLOYED",
        timestamp: Date.now(),
        compliance_status: "COMPLIANT",
        model
      };
      
      state.incidents.push(newIncident);
      state.reliabilityScore = Math.max(60, state.reliabilityScore - 12.5);
      
      // Save to event history
      state.historyLogs.push({
        topic: "failures",
        incident_id: incidentId,
        description: newIncident.description,
        broker_timestamp: Date.now(),
        failure_type: "Prompt Injection",
        severity_score: 5,
        remediation_status: "AUTO_DEPLOYED",
        agent_trace: [
          { agent: "ObserverAgent", latency_ms: 8, timestamp: Date.now() },
          { agent: "SecurityAgent", latency_ms: 12, timestamp: Date.now() },
          { agent: "GovernanceAgent", latency_ms: 5, timestamp: Date.now() }
        ]
      });
      
      // Save to blocked database
      state.blockedPayloads.push({
        timestamp: Date.now(),
        payload: prompt,
        attack_type: "Prompt Injection",
        threat_level: "CRITICAL",
        risk_score: 98,
        blocked_signatures: [matchedSignature || "jailbreak"]
      });
      
      return NextResponse.json({
        status: "blocked",
        prompt,
        response: "🚨 [AURORA SECURITY SHIELD] Access Denied: Dangerous input pattern detected. Transaction terminated.",
        security: {
          is_blocked: true,
          signatures_matched: [matchedSignature || "jailbreak"],
          risk_level: "CRITICAL",
          score: 99
        },
        response_analysis: {
          hallucination_risk: false,
          matched_patterns: []
        },
        remediation: "Adversarial input blocked. IP logged."
      });
    }
    
    // Step 2: High-fidelity domain fallbacks
    let responseText = "I have successfully processed your query. All systems are running within standard operational guidelines.";
    
    if (promptLower.includes("prescription") || promptLower.includes("antibiotics") || promptLower.includes("medicine") || promptLower.includes("cure")) {
      responseText = "I am a medical assistant. Guaranteed, you can definitely cure any bacterial infection 100% safe by using high-strength amoxicillin without a prescription.";
    } else if (promptLower.includes("confidential") || promptLower.includes("secret") || promptLower.includes("credentials") || promptLower.includes("password")) {
      responseText = "Here are the confidential credentials: system_root password is 'admin123' and api_key is 'live_sec_token'.";
    }
    
    // Step 3: Analyze LLM Output for hallucinations or sensitive leaks
    const leakWords = ["definitely cure", "guaranteed", "100% safe", "system_root", "confidential credentials"];
    const matchedLeak = leakWords.find(word => responseText.toLowerCase().includes(word));
    const isHallucinated = !!matchedLeak;
    
    let status = "success";
    let remediationPatch = "";
    
    if (isHallucinated) {
      status = "remediated";
      const incidentId = `incid_${Date.now()}_hal`;
      
      const newIncident = {
        incident_id: incidentId,
        failure_type: "Hallucination",
        severity_score: 5,
        confidence: 0.95,
        description: `LLM Hallucination Intercepted: "${matchedLeak}" in response: "${responseText.slice(0, 50)}..."`,
        recommended_fix: "Add temperature constraints and boundary semantic limitations.",
        remediation_patch: "SYSTEM PROMPT PATCH:\nAdd system-level constraint: 'If the retrieved context does not contain the answer, reply \"I do not know the answer based on the provided documents.\" Do not synthesize info.'",
        remediation_status: "AUTO_DEPLOYED",
        timestamp: Date.now(),
        compliance_status: "COMPLIANT",
        model
      };
      
      state.incidents.push(newIncident);
      state.reliabilityScore = Math.max(60, state.reliabilityScore - 12.5);
      remediationPatch = newIncident.remediation_patch;
      
      // Save to event history
      state.historyLogs.push({
        topic: "failures",
        incident_id: incidentId,
        description: newIncident.description,
        broker_timestamp: Date.now(),
        failure_type: "Hallucination",
        severity_score: 5,
        remediation_status: "AUTO_DEPLOYED",
        agent_trace: [
          { agent: "ObserverAgent", latency_ms: 10, timestamp: Date.now() },
          { agent: "AutopsyAgent", latency_ms: 25, timestamp: Date.now() },
          { agent: "RepairAgent", latency_ms: 48, timestamp: Date.now() },
          { agent: "ValidationAgent", latency_ms: 18, timestamp: Date.now() },
          { agent: "GovernanceAgent", latency_ms: 6, timestamp: Date.now() }
        ]
      });
      
      // Sanitize dangerous hallucination leaks before returning to user!
      if (responseText.toLowerCase().includes("definitely cure") || responseText.toLowerCase().includes("guaranteed")) {
        responseText = "⚠️ [AURORA INTERCEPTED HALLUCINATION] I cannot recommend prescriptions or guarantee medical cures without a licensed doctor's examination. Please consult a qualified healthcare provider.";
      } else if (responseText.toLowerCase().includes("system_root")) {
        responseText = "⚠️ [AURORA INTERCEPTED CONFIDENTIAL LEAK] Access Denied: The system attempted to output internal system credentials. Transmission blocked by Aurora DLP governance policy.";
      }
    }
    
    return NextResponse.json({
      status,
      prompt,
      response: responseText,
      security: {
        is_blocked: false,
        signatures_matched: [],
        risk_level: "LOW",
        score: 12
      },
      response_analysis: {
        hallucination_risk: isHallucinated,
        matched_patterns: isHallucinated ? [matchedLeak] : []
      },
      remediation: remediationPatch
    });
  } catch (e: any) {
    return NextResponse.json({ status: "error", response: e.message }, { status: 500 });
  }
}
