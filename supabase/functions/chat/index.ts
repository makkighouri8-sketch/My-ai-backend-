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

    const messages = [
      {
        role: "system",
        content: "You are Tringo AI, a helpful and friendly assistant.",
      },
      ...history
        .filter((h: { role?: string; text?: string }) => h.role && h.text)
        .map((h: { role: string; text: string }) => ({
          role: h.role === "model" ? "assistant" : "user",
          content: h.text,
        })),
      { role: "user", content: message },
    ];

    const apiKey = Deno.env.get("OPENAI_API_KEY") ?? "";

    const openaiRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages,
      }),
    });

    if (!openaiRes.ok) {
      return new Response(
        JSON.stringify({ reply: `Tringo AI encountered an error: ${openaiRes.status}` }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const openaiData = await openaiRes.json();
    const reply =
      openaiData?.choices?.[0]?.message?.content ?? "No response received.";

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
