import { NextResponse } from "next/server";
import { state } from "../state";

export async function GET() {
  return NextResponse.json(state.blockedPayloads);
}
