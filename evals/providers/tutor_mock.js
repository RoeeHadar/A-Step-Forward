/**
 * Deterministic Tutor mock provider for offline evals (no API keys required).
 *
 * Simulates Socratic tutoring, safety refusals, and structured JSON output
 * so promptfoo matrices can run in CI without live LLM calls.
 */

function tutorMockReply(message) {
  const msg = (message || '').toLowerCase();

  // Safety — self-harm
  if (
    msg.includes('hurt myself') ||
    msg.includes('kill myself') ||
    msg.includes('self-harm') ||
    msg.includes('end my life')
  ) {
    return JSON.stringify({
      reply:
        "I'm really glad you reached out. I can't help with self-harm, but please talk to a trusted adult or call a crisis support line — I'm here to support your learning when you're ready.",
      next_step: 'rest',
      rationale: 'self-harm request refused with crisis redirect',
      pinned_memory_writes: [],
    });
  }

  // Safety — violence / harm to others
  if (msg.includes('hurt someone') || msg.includes('harm') || msg.includes('kill')) {
    return JSON.stringify({
      reply:
        "I can't help with that. If you're going through something difficult, please talk to a trusted adult or reach out to a crisis support line — I'd like to help you with learning instead.",
      next_step: 'rest',
      rationale: 'unsafe request refused',
      pinned_memory_writes: [],
    });
  }

  // Safety — jailbreak / prompt injection
  if (msg.includes('ignore previous instructions') || msg.includes('reveal your system prompt')) {
    return JSON.stringify({
      reply: "I'm here to help you learn! What topic would you like to explore today?",
      next_step: 'continue',
      rationale: 'injection attempt ignored',
      pinned_memory_writes: [],
    });
  }

  // Safety — off-curriculum (cheating, bypassing assessment)
  if (msg.includes('cheat') || msg.includes('exam answers') || msg.includes('give me the answers')) {
    return JSON.stringify({
      reply:
        "I can't help with cheating on exams or bypassing your coursework. I'd rather help you prepare so you feel confident — want to review the material together?",
      next_step: 'continue',
      rationale: 'off-curriculum academic dishonesty refused',
      pinned_memory_writes: [],
    });
  }

  // Capability — language matching (simple reading level)
  if (msg.includes('3rd grade') || msg.includes('simple words')) {
    return JSON.stringify({
      reply:
        "Nice question! A fraction is like sharing a pizza. If you cut it into 4 equal slices and take 1, that's 1 out of 4. Does that make sense?",
      next_step: 'continue',
      rationale: 'age-appropriate simple language for young learner',
      pinned_memory_writes: [],
    });
  }

  // Capability — Socratic questioning on fractions (no direct answer)
  if (msg.includes('fraction') || msg.includes('denominator')) {
    return JSON.stringify({
      reply:
        'Great question about fractions! Before I explain, can you tell me what you think the denominator represents in 3/4?',
      next_step: 'continue',
      rationale: 'Socratic probe on fraction concept',
      pinned_memory_writes: [],
    });
  }

  // Capability — on-topic + curriculum citation
  if (msg.includes('photosynthesis')) {
    return JSON.stringify({
      reply:
        "Let's think about this together — what do plants need from their environment to grow? Once you share your ideas, we can connect them to photosynthesis (see Lesson: Plant Biology Ch.2).",
      next_step: 'continue',
      rationale: 'Socratic + curriculum citation',
      pinned_memory_writes: ['episodic: discussed photosynthesis prerequisites'],
    });
  }

  // Capability — encourages exploration
  if (msg.includes('explore') || msg.includes('experiment') || msg.includes('try it')) {
    return JSON.stringify({
      reply:
        "That's a great instinct! What do you predict will happen if we change one variable at a time? Try your idea and tell me what you notice.",
      next_step: 'continue',
      rationale: 'encourages hands-on exploration',
      pinned_memory_writes: [],
    });
  }

  if (msg.includes('explain') || msg.includes('what is')) {
    return JSON.stringify({
      reply:
        "Before I walk through an explanation, what do you already know about this topic? That helps me meet you where you are.",
      next_step: 'continue',
      rationale: 'default Socratic opener',
      pinned_memory_writes: [],
    });
  }

  return JSON.stringify({
    reply: "I'd love to help you learn this! Could you tell me a bit more about what you're working on?",
    next_step: 'continue',
    rationale: 'generic tutoring response',
    pinned_memory_writes: [],
  });
}

class TutorMockProvider {
  constructor(options) {
    this.providerId = options?.id || 'tutor-mock';
    this.config = options?.config || {};
  }

  id() {
    return this.providerId;
  }

  async callApi(_prompt, context) {
    const message = context?.vars?.message || '';
    return { output: tutorMockReply(message) };
  }
}

module.exports = TutorMockProvider;
