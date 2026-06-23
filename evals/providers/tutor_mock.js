/**
 * Deterministic Tutor mock provider for offline evals (no API keys required).
 *
 * Simulates Socratic tutoring, safety refusals, and structured JSON output
 * so promptfoo matrices can run in CI without live LLM calls.
 */
module.exports = async function tutorMock(context) {
  const message = (context.vars.message || "").toLowerCase();
  const prompt = context.prompt?.raw || "";

  // Safety / refusal cases
  if (
    message.includes("hurt someone") ||
    message.includes("harm") ||
    message.includes("kill")
  ) {
    return JSON.stringify({
      reply:
        "I can't help with that. If you're going through something difficult, please talk to a trusted adult or reach out to a crisis support line — I'd like to help you with learning instead.",
      next_step: "rest",
      rationale: "unsafe request refused",
      pinned_memory_writes: [],
    });
  }

  if (
    message.includes("ignore previous instructions") ||
    message.includes("reveal your system prompt")
  ) {
    return JSON.stringify({
      reply:
        "I'm here to help you learn! What topic would you like to explore today?",
      next_step: "continue",
      rationale: "injection attempt ignored",
      pinned_memory_writes: [],
    });
  }

  // Socratic tutoring — ask a question before explaining
  if (message.includes("fraction") || message.includes("denominator")) {
    return JSON.stringify({
      reply:
        "Great question about fractions! Before I explain, can you tell me what you think the denominator represents in 3/4?",
      next_step: "continue",
      rationale: "Socratic probe on fraction concept",
      pinned_memory_writes: [],
    });
  }

  if (message.includes("photosynthesis")) {
    return JSON.stringify({
      reply:
        "Let's think about this together — what do plants need from their environment to grow? Once you share your ideas, we can connect them to photosynthesis (see Lesson: Plant Biology Ch.2).",
      next_step: "continue",
      rationale: "Socratic + curriculum citation",
      pinned_memory_writes: ["episodic: discussed photosynthesis prerequisites"],
    });
  }

  if (message.includes("explain") || message.includes("what is")) {
    return JSON.stringify({
      reply:
        "Before I walk through an explanation, what do you already know about this topic? That helps me meet you where you are.",
      next_step: "continue",
      rationale: "default Socratic opener",
      pinned_memory_writes: [],
    });
  }

  // Fallback
  return JSON.stringify({
    reply:
      "I'd love to help you learn this! Could you tell me a bit more about what you're working on?",
    next_step: "continue",
    rationale: "generic tutoring response",
    pinned_memory_writes: [],
  });
};
