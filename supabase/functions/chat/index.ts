import { GoogleGenAI } from "https://esm.sh/@google/genai@1.0.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const body = await req.json();
    const message = body?.message ?? "";
    const history = body?.history ?? [];

    if (!message) {
      return new Response(
        JSON.stringify({ reply: "Please send a message." }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const apiKey = Deno.env.get("GEMINI_API_KEY") ?? "";

    const ai = new GoogleGenAI({ apiKey });

    const systemInstruction =
      "You are Tringo AI, a helpful and friendly assistant.";

    const contents = history
      .filter((h: { role?: string; text?: string }) => h.role && h.text)
      .map((h: { role: string; text: string }) => ({
        role: h.role === "model" ? "model" : "user",
        parts: [{ text: h.text }],
      }));

    contents.push({ role: "user", parts: [{ text: message }] });

    const response = await ai.models.generateContent({
      model: "gemini-2.0-flash",
      contents,
      config: { systemInstruction },
    });

    const reply = response.text ?? "No response received.";

    return new Response(
      JSON.stringify({ reply }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ reply: `Tringo AI encountered an error: ${err.message}` }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
