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

    const contents = [
      ...history
        .filter((h: { role?: string; text?: string }) => h.role && h.text)
        .map((h: { role: string; text: string }) => ({
          role: h.role === "model" ? "model" : "user",
          parts: [{ text: h.text }],
        })),
      { role: "user", parts: [{ text: message }] },
    ];

    const apiKey = Deno.env.get("GEMINI_API_KEY") ?? "";

    const geminiRes = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents }),
      },
    );

    if (!geminiRes.ok) {
      const errText = await geminiRes.text();
      return new Response(
        JSON.stringify({ reply: `Tringo AI encountered an error: ${geminiRes.status}` }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const geminiData = await geminiRes.json();
    const reply =
      geminiData?.candidates?.[0]?.content?.parts?.[0]?.text ?? "No response received.";

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
