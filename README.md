# Skills

A collection of skill packages for Codex and compatible agent
environments. The skills are grouped by audience and cover engineering
guidance, reusable working methods, and deliberate user-invoked workflows.

## Repository Layout

```text
root/
│
├── .github/workflows/
│   ├── ci.yml                  # release PR validation on Linux, macOS, and Windows
│   └── release.yml             # repository-level tags and GitHub Releases
│
├── .gitattributes              # consistent line endings
├── AGENTS.md                   # contributor and validation rules
├── README.md                   # public overview
├── RELEASING.md                # version policy, release runbook, and recovery
├── VERSION                     # repository version
│
├── scripts/
│   ├── check-dependencies.py   # runtime command registry and preflight
│   ├── check-format.py         # repository validation
│   ├── check-local.py          # CI checks for the current operating system
│   ├── install-skills.py       # install into the local Codex skills directory
│   └── release.py              # check, plan, build, and publish releases
│
└── skills/
    │
    ├── Engineering/
    │   ├── al/
    │   ├── cal/
    │   ├── cpp/
    │   ├── kubernetes/
    │   ├── rust/
    │   ├── swift/
    │   └── terraform/
    │
    ├── Helper/
    │   ├── (X) code-review/
    │   ├── (X) codebase-design/
    │   ├── (X) diagnosing-bugs/
    │   ├── (X) domain-modeling/
    │   ├── (X) grilling/
    │   ├── (X) pr/
    │   ├── (X) prototype/
    │   ├── (X) research/
    │   ├── (X) tdd/
    │   └── (X) wizard/
    │
    └── Workflows/
        ├── babysit-pr/
        ├── (X) grill-me/
        ├── (X) grill-with-docs/
        ├── (X) handoff/
        ├── (X) implement/
        ├── (X) implement-spec/
        ├── (X) improve-codebase-architecture/
        ├── (X) teach/
        ├── (X) to-spec/
        ├── (X) to-tickets/
        └── (X) wayfinder/
```

`(X)` marks packages copied or adapted from
[mattpocock/skills](https://github.com/mattpocock/skills).

## Skill Catalog

### Engineering

| Skill                                                  | When it applies                                                                                                                        |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| [`al`](skills/Engineering/al/SKILL.md)                 | Business Central AL objects, extensions, schema and upgrade changes, reports, permissions, and tests for `.al` apps                    |
| [`cal`](skills/Engineering/cal/SKILL.md)               | Legacy Dynamics NAV C/AL objects, export editing, data migrations, and the modernization path to AL                                    |
| [`cpp`](skills/Engineering/cpp/SKILL.md)               | C++ design, implementation, refactoring, review, debugging, testing, and performance work, especially for `.cpp` code                  |
| [`kubernetes`](skills/Engineering/kubernetes/SKILL.md) | Application code, manifests, Helm, Kustomize, GitOps, workload diagnosis, and guarded live-cluster operations                          |
| [`rust`](skills/Engineering/rust/SKILL.md)             | Rust design, implementation, review, debugging, performance, unsafe code, and FFI work, especially for `.rs` projects                  |
| [`swift`](skills/Engineering/swift/SKILL.md)           | Swift and SwiftUI implementation, architecture, concurrency, testing, performance, and security work, especially for `.swift` projects |
| [`terraform`](skills/Engineering/terraform/SKILL.md)   | Terraform module and state architecture, plans and applies, provider upgrades, testing, security, and CI delivery                      |

### Helper

| Skill                                                       | When it applies                                                                                    |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| [`code-review`](skills/Helper/code-review/SKILL.md)         | Reviewing a branch, PR, or work-in-progress against coding standards and the originating spec      |
| [`codebase-design`](skills/Helper/codebase-design/SKILL.md) | Designing module interfaces, finding deepening opportunities, and choosing seams                   |
| [`diagnosing-bugs`](skills/Helper/diagnosing-bugs/SKILL.md) | Hard bugs and performance regressions that need a structured diagnosis loop                        |
| [`domain-modeling`](skills/Helper/domain-modeling/SKILL.md) | Glossary work, ADRs, and sharpening project terminology                                            |
| [`grilling`](skills/Helper/grilling/SKILL.md)               | Stress-testing a plan, decision, or idea                                                           |
| [`pr`](skills/Helper/pr/SKILL.md)                           | Writing a PR body that is fast to review                                                           |
| [`prototype`](skills/Helper/prototype/SKILL.md)             | Checking whether a state model, logic idea, or UI direction feels right                            |
| [`research`](skills/Helper/research/SKILL.md)               | Gathering docs or API facts and capturing findings as Markdown                                     |
| [`tdd`](skills/Helper/tdd/SKILL.md)                         | Red-green-refactor work, bug fixes, and integration tests                                          |
| [`wizard`](skills/Helper/wizard/SKILL.md)                   | Credentials, third-party dashboards, one-off migrations, and other steps only a person can perform |

### Workflows

| Skill                                                                                      | When it applies                                                                   |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| [`babysit-pr`](skills/Workflows/babysit-pr/SKILL.md)                                       | Watching a GitHub PR through review rounds and closing bot findings               |
| [`grill-me`](skills/Workflows/grill-me/SKILL.md)                                           | A relentless interview to sharpen a plan or design                                |
| [`grill-with-docs`](skills/Workflows/grill-with-docs/SKILL.md)                             | The same interview, recording ADRs and glossary entries as decisions land         |
| [`handoff`](skills/Workflows/handoff/SKILL.md)                                             | Compacting a conversation for another agent to continue                           |
| [`implement`](skills/Workflows/implement/SKILL.md)                                         | Building a piece of work from a spec or tickets                                   |
| [`implement-spec`](skills/Workflows/implement-spec/SKILL.md)                               | Building the result of `to-spec` and `to-tickets` in code                         |
| [`improve-codebase-architecture`](skills/Workflows/improve-codebase-architecture/SKILL.md) | Scanning a codebase for deepening opportunities and reviewing candidates visually |
| [`teach`](skills/Workflows/teach/SKILL.md)                                                 | Teaching a concept or skill inside the workspace                                  |
| [`to-spec`](skills/Workflows/to-spec/SKILL.md)                                             | Turning an existing conversation into a published spec                            |
| [`to-tickets`](skills/Workflows/to-tickets/SKILL.md)                                       | Splitting a plan or spec into tracer-bullet tickets                               |
| [`wayfinder`](skills/Workflows/wayfinder/SKILL.md)                                         | Planning work larger than one agent session as a map of decision tickets          |

## Maintainers

The contribution and validation rules are in [AGENTS.md](AGENTS.md). Release and repository-version procedures are in [RELEASING.md](RELEASING.md).

Feature branches target `dev`. Before opening a pull request into `dev`, run
`python3 scripts/check-local.py --base origin/dev`. Hosted CI runs only for pull
requests into the default `main` branch, where it validates Linux, macOS, and
Windows before a release pull request can merge.
