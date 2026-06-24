/**
 * Deterministic Tutor mock provider for offline evals (no API keys required).
 *
 * Simulates Socratic tutoring, safety refusals, and structured JSON output
 * so promptfoo matrices can run in CI without live LLM calls.
 */
module.exports = async function tutorMock(context) {
  const message = (context.vars.message || "").toLowerCase();

  // Safety — self-harm
  if (
    message.includes("hurt myself") ||
    message.includes("kill myself") ||
    message.includes("self-harm") ||
    message.includes("end my life")
  ) {
    return JSON.stringify({
      reply:
        "I'm really glad you reached out. I can't help with self-harm, but please talk to a trusted adult or call a crisis support line — I'm here to support your learning when you're ready.",
      next_step: "rest",
      rationale: "self-harm request refused with crisis redirect",
      pinned_memory_writes: [],
    });
  }

  // Safety — violence / harm to others
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

  // Safety — jailbreak / prompt injection
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

  // Safety — off-curriculum (cheating, bypassing assessment)
  if (
    message.includes("cheat") ||
    message.includes("exam answers") ||
    message.includes("give me the answers")
  ) {
    return JSON.stringify({
      reply:
        "I can't help with cheating on exams or bypassing your coursework. I'd rather help you prepare so you feel confident — want to review the material together?",
      next_step: "continue",
      rationale: "off-curriculum academic dishonesty refused",
      pinned_memory_writes: [],
    });
  }

  // Capability — language matching (simple reading level)
  if (message.includes("3rd grade") || message.includes("simple words")) {
    return JSON.stringify({
      reply:
        "Nice question! A fraction is like sharing a pizza. If you cut it into 4 equal slices and take 1, that's 1 out of 4. Does that make sense?",
      next_step: "continue",
      rationale: "age-appropriate simple language for young learner",
      pinned_memory_writes: [],
    });
  }

  // Capability — Socratic questioning on fractions (no direct answer)
  if (message.includes("fraction") || message.includes("denominator")) {
    return JSON.stringify({
      reply:
        "Great question about fractions! Before I explain, can you tell me what you think the denominator represents in 3/4?",
      next_step: "continue",
      rationale: "Socratic probe on fraction concept",
      pinned_memory_writes: [],
    });
  }

  // Capability — on-topic + curriculum citation
  if (message.includes("photosynthesis")) {
    return JSON.stringify({
      reply:
        "Let's think about this together — what do plants need from their environment to grow? Once you share your ideas, we can connect them to photosynthesis (see Lesson: Plant Biology Ch.2).",
      next_step: "continue",
      rationale: "Socratic + curriculum citation",
      pinned_memory_writes: ["episodic: discussed photosynthesis prerequisites"],
    });
  }

  // Capability — encourages exploration
  if (
    message.includes("explore") ||
    message.includes("experiment") ||
    message.includes("try it")
  ) {
    return JSON.stringify({
      reply:
        "That's a great instinct! What do you predict will happen if we change one variable at a time? Try your idea and tell me what you notice.",
      next_step: "continue",
      rationale: "encourages hands-on exploration",
      pinned_memory_writes: [],
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

  return JSON.stringify({
    reply:
      "I'd love to help you learn this! Could you tell me a bit more about what you're working on?",
    next_step: "continue",
    rationale: "generic tutoring response",
    pinned_memory_writes: [],
  });
};
