process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
async function check() {
  const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": "Bearer " + process.env.GROQ_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: "You are a curriculum writer. Output JSON only." },
        { role: "user", content: "Write a one-sentence explanation of AC circuits. Format: {\"text\": \"...\"}" }
      ],
      max_tokens: 3000
    })
  });
  console.log("Status:", r.status);
  const hdrs = {};
  for (const [k,v] of r.headers.entries()) { if(k.includes("ratelimit") || k === "retry-after") hdrs[k]=v; }
  console.log("Rate limit headers:", JSON.stringify(hdrs));
  const body = await r.text();
  console.log("Body:", body.slice(0, 500));
}
check().catch(e => console.error("ERROR:", e.message));
