import { NextResponse } from "next/server";
import { state } from "../state";

export async function POST() {
  state.incidents = [];
  state.historyLogs = [];
  state.blockedPayloads = [];
  state.reliabilityScore = 100;
  
  return NextResponse.json({
    success: true,
    message: "Database successfully flushed"
  });
}
