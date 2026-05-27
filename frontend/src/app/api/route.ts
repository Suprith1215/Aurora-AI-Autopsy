import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    system: "AURORA API Gateway Core",
    status: "ONLINE",
    version: "5.0.0",
    endpoints: [
      "/api/telemetry",
      "/api/history",
      "/api/blocked",
      "/api/analyze"
    ]
  });
}
