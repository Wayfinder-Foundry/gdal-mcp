---
description: Catch-all planning workflow.
---

id: plan
version: 1
enabled: true
priority: high
trigger:
  phrases_any:
    - "plan"
    - "make a plan"
    - "rubber duck this"
    - "outline approach"
    - "write a plan"
options:
  dry_run: false
  create_branch: false           # set true to branch when saving notes into a repo
  branch_prefix: "plan/"
  notes_dir: ".plans"            # where markdown lands (created if missing)
  filename_prefix: "plan"        # file name seed; timestamp appended
  include_git_snapshot: true
  include_repo_context: true     # pull structural context when helpful
  include_library_lookups: true  # only when uncertainty appears
  push_commit: false
  markdown_tone: "succinct"      # or: narrative
  # model autonomy settings
  capture_threshold: "normal"    # "minimal" | "normal" | "rich"
  # caps & guards
  max_reflection_rounds: 2
  max_lookup_items: 5

state:
  plan_path: null
  branch: null
  summary_bullets: []
  open_questions: []
  decisions: []
  next_steps: []

steps:

  # 0) Optional repo hygiene
  - name: preflight.git
    when: "{{options.include_git_snapshot}}"
    tool: git-mcp
    run:
      - status
      - current_branch
      - detect_default_branch
    on_result:
      - if: "{{options.create_branch and (result.on_default_branch or result.current_branch in ['main','master'])}}"
        then:
          - create_branch "{{options.branch_prefix}}{{date:%Y%m%d-%H%M}}"
          - set: state.branch = "{{last_result.new_branch}}"
      - else:
          - set: state.branch = "{{result.current_branch}}"

  # 1) Seed a lightweight “thinking plan” via sequential-thinking
  - name: plan.seed
    tool: sequential-thinking
    run:
      - reflect
        prompt: |
          Create a brief plan scaffold for rubber-ducking.
          Include:
          - problem statement (1–2 sentences)
          - success criteria (bullet list, observable)
          - options (2–3) with pros/cons; select one with reason
          - unknowns / risks / assumptions
          - first 5 concrete next steps
          - “library/API certainty needed?” yes/no + topics
          - “repo context needed?” yes/no + targets
          Keep it {{options.markdown_tone}}.
      - extract bullets to:
          summary -> state.summary_bullets
          open_questions -> state.open_questions
          decisions -> state.decisions
          next_steps -> state.next_steps
      - save_plan path=".tmp/plan_seed.yaml"

  # 2) Optional library/API certainty (Context7), only if plan asks for it
  - name: research.context7
    when: "{{options.include_library_lookups}}"
    tool: context7
    run_if:
      - "plan_seed indicates library/API certainty needed"
    run:
      - lookup_many from_topics_file=".tmp/plan_seed.yaml" limit="{{options.max_lookup_items}}"
      - summarize usage="concise" bullets=true attach_to=".tmp/lookups.md"

  # 3) Optional repo structure grounding (Serena), only if helpful
  - name: context.serena
    when: "{{options.include_repo_context}}"
    tool: serena
    run_if:
      - "plan_seed indicates repo context needed"
    run:
      - index_project_if_needed
      - get_symbols_overview limit=200
      - structural_summary max_files=80
      - infer_related_files topics_from=".tmp/plan_seed.yaml"
      - save_overview path=".tmp/repo_context.md"

  # 4) Rubber-ducking pass (brief reflection loops)
  - name: reflect.duck
    loop:
      count: "{{options.max_reflection_rounds}}"
      steps:
        - tool: sequential-thinking
          run:
            - reflect
              prompt: |
                Re-express the chosen approach to an imaginary peer (“rubber duck”):
                - explain rationale in plain language
                - challenge your own assumptions
                - address top unknowns one-by-one
                - if any answer remains uncertain, mark it as OPEN
                Keep it concise; prefer actionable bullets.
            - append_reflections to=".tmp/duck.md"

  # 5) Assemble Markdown plan (model decides what’s worth capturing)
  - name: plan.compose_markdown
    tool: sequential-thinking
    run:
      - synthesize
        prompt: |
          Compose a single Markdown document for durable reference.
          Use sections: Title, Summary, Context, Decision, Options (brief), Unknowns & Risks,
          Plan & Next Steps, Repo Context (if present), Library Notes (if present), Appendix.
          Use the content from .tmp/plan_seed.yaml, .tmp/duck.md,
          and optionally .tmp/repo_context.md and .tmp/lookups.md.
          Respect capture_threshold="{{options.capture_threshold}}" to decide how much detail to keep.
          Favor signal over noise. Trim low-value repetition.
      - write_markdown
        to_dir="{{options.notes_dir}}"
        filename="{{options.filename_prefix}}-{{date:%Y%m%d-%H%M}}.md"
      - set: state.plan_path = "{{last_result.path}}"

  # 6) Persist high-level summary to ConPort (non-blocking)
  - name: memory.conport
    tool: conport
    continue_on_error: true
    run:
      - remember
        text: >
          PLAN created at {{now}} ({{state.plan_path}}) on branch {{state.branch}}.
          Summary: {{state.summary_bullets}}
          Decisions: {{state.decisions}}
          Next steps: {{state.next_steps}}
          Open questions: {{state.open_questions}}

  # 7) Optional git snapshot commit (adds the Markdown note)
  - name: vcs.snapshot
    when: "{{options.include_git_snapshot}}"
    tool: git-mcp
    run:
      - add "{{state.plan_path}}"
      - commit
        message: >
          plan: {{basename(state.plan_path)}} — initial plan, decisions, and next steps
      - push when="{{options.push_commit}}"

  # 8) Output final summary
  - name: out.summary
    tool: sequential-thinking
    run:
      - summarize
        prompt: |
          Produce a brief status:
          - path of plan
          - 3 key decisions
          - 3 next steps
          - any OPEN questions
          Keep it ultra concise.
