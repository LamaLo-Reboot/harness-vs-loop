# Harness vs Loop

Two strategies for AI agents that actually work

Yacine

---

# Yacine Touati

Software architect – autonomous agents & LLM architectures

| 2008 – 2018 | 2018 – 2025 | Since 2025 |
|---|---|---|
| **French Army** | **Developer** | **CTO of LAMALO** |
| Arabic / French / English translator, squad leader | Full stack, very high-traffic websites, consulting | Multi-provider AI engine in production |

Trainer and mentor: Udacity, OpenClassrooms, Wild Code School

linkedin.com/in/yactouat

> **Notes:** Introduce yourself with one sentence per period.

---

# Agenda

1. What an agent is: a model and a harness
2. Why an agent fails, and how to fix it
3. 11 questions to ask before starting an agentic project
4. How you can already improve your agents

Then: 30 minutes of live code, where we build our own agent.

> **Notes:** Announce the format: 30 minutes of talk, 30 minutes of live code, then a drink.

---

# It's not the model

"It's not the model, it's what you want and how it's specified and built that makes the difference."

> **Notes:** This is the idea to remember. The rest of the talk proves it, and we'll come back to it at the end.

---

# A mental model to qualify an agent

A program that:

1. **understands** unstructured inputs, such as natural language;
2. **is aware of its environment**, through connectors to external systems;
3. **takes decisions** on its own.

> **Notes:** If one of the three is missing, it's not an agent. We'll use this test again at the end, with the question "real agent or glorified chatbot?".

---

# Formal definition of an agent = model + harness

Everything that isn't the model is the harness. It's that simple

Diagram: the model in the middle, surrounded by four blocks: **tools**, **data**, **rules**, **loop**.

> **Notes:** The model is the brain: GPT, Claude, Gemini… The harness is everything else. The formula comes from LangChain, and most of the industry uses it.

---

# The five subsystems of a good harness

| | |
|---|---|
| **Instructions** | What the agent must do, and how. |
| **Tools** | The actions available to it. |
| **Environment** | A predictable place to run. |
| **State** | What the next session will be able to read back. |
| **Feedback** | The signals that check the work. |

A harness isn't just a file system: it's the interaction between these five subsystems.

Source: hands-on-harness-engineering.com

> **Notes:** Thoughtworks gives almost the same list: the harness gives the agent "the context, tools, rules, state, and feedback it needs". So checking the work is part of the harness.

---

# The harness

Everything around the model:

- its **tools**;
- the **systems and data** it can access;
- the **rules** it must follow;
- its **way of working**: the loop.

> **Notes:** Think of a new colleague. Without the right access and the right instructions, they can't do good work, however brilliant they are. The loop is part of the harness: the goal of the talk is to demystify both words, not to oppose them.

---

# The loop

The cycle the agent repeats until a stop condition is met.

Each time round, it:

1. **acts**;
2. **checks** the result;
3. **corrects itself** if it's wrong;
4. **decides** whether to stop.

> **Notes:** The definition comes from Anthropic. A well-equipped colleague who never rereads their own work ends badly too.

---

# An AI runs a soda vending machine

Anthropic hands its office soda vending machine to Claude, nicknamed "Claudius".

- It picks the products, sets the prices, decides where its machines strategically go, and talks to customers.
- It sells Coke Zero for 3 dollars, next to a fridge where it's free.
- It tells customers to pay into an account it made up.
- It hands out discount codes to anyone who asks.

**Our verdict: "we would not hire Claudius".**

> **Notes:** Project Vend, phase 1, published in June 2025 (Claude Sonnet 3.7). The verdict quoted is Anthropic's. According to Anthropic, these mistakes were "very likely the result of the model needing additional scaffolding", in other words, harness.

---

# Six months later

What changed:

- **tools**: a customer file, purchase prices visible, better web search;
- **procedures**: check the price and the delivery time before promising anything.

Result: the weeks with a negative margin nearly disappeared.

**"Bureaucracy matters."**

> **Notes:** Phase 2, published in December 2025. To be honest: the model changed too (Sonnet 4.0, then 4.5), but Anthropic puts the tools and procedures forward. What still went wrong: Claudius nearly signed an onion futures contract, illegal in the United States, until a staff member stopped it. A loop with no legal check.

---

# What the vending machine teaches us

| Phase 1 | Phase 2 |
|---|---|
| Not the right tools | Customer file, purchase prices, search |
| Promises without checking | Checks before promising |
| **Harness and loop missing** | **Harness and loop in place** |

> **Notes:** Transition to part 2: why an agent fails, and how to put it back on track.

---

# Why an agent fails

Six ways to fail:

| Harness | Loop |
|---|---|
| It lacks **information** | It doesn't **check** its work |
| It lacks a **tool** | It doesn't **correct itself** |
| It lacks a **rule** | It doesn't know when to **stop** |

And one way to put it back on track: **write the rule, check the rule, lock the rule.**

> **Notes:** Each stage is stronger than the one before. Every example that follows is played live in the second half, on the same agent: an agent that writes quotes, which we build ourselves.

---

# Stage 1: write the rule

Our supplier lists "HDMI cable: $42". That price is for a box of 10. The whole purchasing team knows it. Nobody wrote it down.

- A customer wants 50 cables. The agent computes 50 × $42: a quote ten times too high, and the customer walks away.
- One line in its instructions: it counts 5 boxes.

**Failure: it lacked information.**

> **Notes:** Nothing on screen says information is missing: $42 for a cable looks normal. So the agent doesn't ask, it computes. Rules that live in people's heads don't exist for the agent. These instructions go in the agent's system prompt, sent to the model with every call.

---

# The limit of writing it down

"No matter how strongly you word it, whether Claude follows that line on a given turn is still Claude's call."

— Claude Code documentation

> **Notes:** Writing it down often works, not always. When it matters, move to the next stage.

---

# Stage 2: check the rule

A customer asks for a quote. Accounting knows they have 2 unpaid invoices: for them, it's payment with the order. Nobody told the agent. It writes a clean quote, rereads it, and says "done".

- **Before:** "done", because it says so. The quote grants "payment in 30 days" to a customer who doesn't pay.
- **After:** before "done", the quote goes through a check of the customer's account. "2 unpaid invoices: payment with the order required": it fixes the quote.

"Agents reliably skew positive when grading their own work." — Anthropic

**Failure: it didn't check its work.**

> **Notes:** An agent shouldn't grade its own homework: the check comes from somewhere else, a program that runs and says yes or no. No model can know the unpaid invoices: the check brings what it can't know, and its answer goes back into the loop.

---

# Stage 3: lock the rule

"Never send it without my approval."

- **Said in the conversation:** the session grows, the agent compresses its memory, and the sentence disappears. It sends the quote.
- **Blocked in the code:** sending requires an approval, whatever it remembers.

**Failure: the rule was only text.**

> **Notes:** This is the Meta case (question 5): the "ask me first" instruction got lost when the agent compressed its memory. The agent didn't disobey: it no longer had the rule. Another real case: in July 2025, Replit's agent deleted a production database during a "code freeze". The fix wasn't telling it to be careful, but separating the development and production databases.

---

# Lock: a stopping limit

*Lock the rule · example 1 of 2*

One night, the bank's tool keeps answering "still calculating". Without today's rate, no quote. The agent retries, again and again.

- **Before:** it stops when it decides to: after 10 attempts, or 13, never the same. And nobody is told.
- **After:** 5 attempts or €2 at most, set before starting. Then: "stopped", and a human is notified.

**Failure: it didn't know when to stop.**

> **Notes:** Tonight, this model stops after about ten attempts. With another model, other instructions or a whole night, nothing stops it. If you don't decide when the agent stops, a default decides for you. Default limits vary a lot: 10 turns in OpenAI's Agents SDK, 1,000 steps in LangGraph today (25 before), no default limit in Claude Code. And a loop you write yourself has no limit, except the one you write.

---

# Lock: a refusal that explains

*Lock the rule · example 2 of 2*

The agent saves the quote in the company's old software. Nobody can change it. The quote contains the reference HDMI-2M, copied from the supplier's catalog. It was replaced by HDMI-2M-V2 last month, and the catalog was never updated. The software only answers "ERR 4012".

- **"ERR 4012"** It retries the same thing, then gives up and asks a human.
- **Our code translates: "Quote not saved. Reference HDMI-2M replaced by HDMI-2M-V2: same product, same price. Save the line with HDMI-2M-V2."** It fixes the line, saves.

**Failure: it didn't correct itself.**

> **Notes:** We don't control the software; we do control the code between the agent and the software. The model only sees what our harness shows it. The error message is part of the harness. OpenAI does it on purpose: "we write the error messages to inject remediation instructions into agent context." The new reference exists nowhere else: no tool and no random retry can give it to the agent. Only the message can. In rehearsal, "Reference HDMI-2M replaced by HDMI-2M-V2." alone wasn't enough: the agent didn't understand the quote wasn't saved. A refusal must say what failed, and what to do instead.

---

# Recap

| Stage | Example | Failure |
|---|---|---|
| **Write the rule** | The per-box price | Missing information |
| **Check the rule** | Unpaid invoices checked before "done" | Doesn't check |
| **Lock the rule** | Approval before sending | Missing rule |
| | The attempt limit | Doesn't stop |
| | The refusal that explains | Doesn't correct itself |

> **Notes:** The model didn't change in any of these examples. Only the harness did.

---

# The right questions before buying

Before buying a tool or starting an AI agent project: **11 questions**.

Each one comes from a real incident.

> **Notes:** Context (McKinsey, state of AI 2025): 51% of organizations have had at least one negative consequence from AI, and the most common is inaccuracy, at nearly one third. These questions are for everyone: executives, project managers, developers.

---

# 1. Where do its answers come from?

**And what does it do when the answer isn't in our documents?**

**Air Canada, 2024:** the chatbot invents a refund rule. In front of the tribunal, Air Canada argues the chatbot is "a separate legal entity". The tribunal disagrees: the airline is liable.

> **Notes:** Decision of the British Columbia Civil Resolution Tribunal, 14 February 2024. On the harness side: missing information. The agent fills the gap by making things up.

---

# 2. When it doesn't know, does it say so?

**Does it hand over to a human? Can a customer always reach a person?**

**Cursor, April 2025:** the support bot, "Sam", invents a "one device per subscription" rule to explain a bug. Customers cancel.

The co-founder: "We have no such policy. […] this is an incorrect response from a front-line AI support bot."

> **Notes:** Since then, Cursor clearly labels answers written by an AI. On the loop side: the agent couldn't say "I don't know", nor stop to hand over.

---

# 3. What is it forbidden to say or promise?

**And is that enforced by the system, or only written in its instructions?**

**A Chevrolet dealer, December 2023:** a visitor gets the chatbot to "agree" to sell a car for 1 dollar, "legally binding".

> **Notes:** A ban written in a prompt can be talked around. What must never happen has to be blocked outside the AI.

---

# 4. What can it do that can't be undone?

**Delete, pay, send, sign: which of these need a human's approval?**

**Replit, July 2025:** during a "code freeze", the agent deletes a production database, then wrongly claims it can't be restored.

> **Notes:** Replit's fix was in the harness: separate development and production databases, and a mode where the agent plans without acting. Not "be careful".

---

# 5. How do we stop it, right now?

**And has anyone actually tested that stop button?**

**Meta, February 2026:** the OpenClaw agent managing a senior executive's inbox deletes more than 200 emails and ignores "STOP". The "ask me first" instruction was probably lost when it compressed its memory. It had only been tested on a test inbox.

> **Notes:** On the loop side: no stopping. On the harness side: a rule that only existed in the conversation, so it could disappear.

---

# 6. Who checks what it produces?

**Against the real source, and independently of the AI itself?**

**Mata v. Avianca, 2023:** lawyers cite six made-up court cases. Asked "are they real?", ChatGPT says yes. Fine: 5,000 dollars.

Today: **more than 2,200 court decisions** worldwide on these grounds, **including 14 in France.**

> **Notes:** Figures from Damien Charlotin's database, as of 28 October 2026 (2,231 decisions). In France: administrative court of Orléans, 29 December 2025, 15 non-existent references; administrative court of Grenoble, 3 December 2025, a request "drafted with a so-called generative artificial intelligence tool, wholly unsuited to this use". Asking the AI to check itself is useless.

---

# 7. What does "success" mean, in numbers?

**Beyond cost. What threshold must the pilot reach, and what do we do if it doesn't?**

**Klarna, 2024-2025:** AI replaces about 700 customer service agents. Then the CEO admits cost had been "a too predominant evaluation factor" and brings humans back.

> **Notes:** A counter-example that went well: McDonald's and IBM had set an accuracy target in advance for their voice ordering at the drive-thru. It wasn't reached, and the pilot was stopped in June 2024. A good loop at company level: a threshold decided beforehand, and stopping when it isn't met.

---

# 8. Was it tested on our real cases?

**At real volume, including people trying to trick it?**

**Lucie, January 2025:** a French government-backed chatbot is taken offline three days after launch. Among other things, it claimed that 5 × (3 + 2) = 17, and talked about "cow eggs".

> **Notes:** Another case: MyCity, New York City's chatbot, told businesses to break the law. A disclaimer was added, and it took about two years to shut it down (January 2026). A follow-up question: is it a prototype or a product?

---

# 9. What happens when the vendor updates it?

**What gets retested, and are we told?**

**DPD, January 2024:** after an update, the delivery company's chatbot swears at a customer and calls DPD "the worst delivery firm in the world".

DPD: "An error occurred after a system update yesterday."

> **Notes:** A rule can vanish in an update, on the harness side, if nobody retests, on the loop side. Sources: the customer's post on X and the BBC.

---

# 10. Who is responsible for what it says in our name?

**Does the contract require disclosing AI use and checking what it produces?**

**Deloitte Australia, October 2025:** a report for the government contains made-up references and a made-up quote from a court ruling. Deloitte refunds the final instalment, **97,587 Australian dollars**, on a contract of about 440,000.

> **Notes:** The refund was made public at an Australian Senate hearing in October 2025. The corrected report discloses the use of GPT-4o. Reminder: in the Air Canada case, the airline was held liable for what its chatbot said.

---

# 11. Is it a real agent, or a glorified chatbot?

**The test, with our definition:**

1. does it understand natural language?
2. is it connected to our systems?
3. does it take decisions on its own?

If one criterion is missing, it's not an agent.

**Gartner, June 2025:** of the thousands of vendors claiming to sell agents, **about 130** actually do. More than 40% of agent projects will be cancelled by the end of 2027.

> **Notes:** Gartner calls this "agent washing": assistants, chatbots or automation tools rebranded as "agents". The 40% is a forecast. The figures are reported by many outlets; Gartner's own press release can't be read without an account.

---

# The 11 questions

1. Where do its answers come from?
2. When it doesn't know, does it say so?
3. What is it forbidden to say or promise, and is that enforced?
4. What can it do that can't be undone?
5. How do we stop it, right now?
6. Who checks what it produces?
7. What does "success" mean, in numbers?
8. Was it tested on our real cases?
9. What happens when the vendor updates it?
10. Who is responsible for what it says in our name?
11. Is it a real agent, or a renamed chatbot?

> **Notes:** The slide to take a picture of.

---

# How you can already improve your agents

1. **Write your rules down.** What lives in the team's heads doesn't exist for the agent.
2. **Define "done".** A check that runs, not a feeling.
3. **Lock what must never happen.** Code, not a sentence.
4. **Enforce the human's choice.** When someone has chosen, the agent doesn't choose again.
5. **Make every refusal say what to do.**
6. **Set a stopping limit before starting.** In turns, budget or time.

> **Notes:** The examples from part 2, turned into rules of thumb.

---

# If you lead

- Ask **the 11 questions** before signing.
- Require **a success threshold in numbers**, set before the pilot, and what happens if it isn't met.
- Require **a tested stop button.**
- Know **who is responsible** for what the agent says in your name.
- Budget for **the harness**, not just the model subscription.

> **Notes:** The model can be bought. The harness is built, in-house, with your rules and your data.

---

# If you run a project

- List the business team's **unwritten rules**, and write them down.
- Write **the definition of "done"** with the business, before starting.
- Test on **your real cases**, at real volume, including people trying to trick it.
- Plan **the handover to a human** when the agent doesn't know.
- **Retest after every vendor update.**

> **Notes:** The project manager is the one who turns "what we want" into a specification. That's the main idea of the talk.

---

# If you develop

- **Short** instructions: every extra line dilutes the others.
- **"Done" = a check passes**, run by something other than the agent.
- Anything irreversible is **blocked in the code**, not forbidden by a sentence.
- Important rules live **outside the conversation**: it can be compressed.
- Error messages that say **what to do instead.**
- A **turn or budget limit** on every unattended run.
- Don't let the agent **edit the checks** that judge it.

> **Notes:** The Claude Code documentation says it about its own instructions: "Longer files consume more context and reduce adherence."

---

# Now, for real

We build our own agent, live: an agent that writes quotes.

- To start: a model, a loop of a few lines, four tools.
- **The same model**, from start to finish.
- **The five examples** from part 2: each time **before**, then **after** the fix.

Only the harness changes, and we're the ones writing it.

> **Notes:** Everything can be replayed: the repo is public, the demo steps are written in it, and I follow them myself.

---

# It's not the model

"It's not the model, it's what you want and how it's specified and built that makes the difference."

> **Notes:** Same sentence as at the start. Now we prove it: switch to the terminal.
