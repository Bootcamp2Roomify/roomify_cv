<!--
PR title should follow this format:

[ROOM-###] <type>: Brief description of the change

Types: feat, fix, docs, refactor, test, chore

Example:
[ROOM-7] docs: Set up computer vision repository and Git workflow
-->

## Before You Start

- [ ] I have read and will follow the Contributing Guide.
- [ ] My branch follows the naming convention: `<type>/descriptive-name`.
- [ ] My PR title follows the format: `[ROOM-###] <type>: description`.
- [ ] My branch includes the latest changes from `develop`.

---

[Brief one-line description of what this PR adds]

#### Summary

- [Main addition or change]
- [Another important change]
- [Third important change]

#### Changes

- New: [List new files, services, models, or directories]
- Modified: [List modified files and explain what changed]
- Removed: [List deleted files or functionality]

#### Implementation

- [Explain key technical decisions]
- [Describe the image-processing or detection logic]
- [Describe request and response changes]
- [Mention assumptions, limitations, or trade-offs]

#### Why

- [Explain why this change is needed]
- [Connect the change to the related Roomify feature or Jira task]

#### Detection or API Changes

- [ ] Added or changed a FastAPI endpoint
- [ ] Added or changed a request or response schema
- [ ] Added or changed computer-vision model integration
- [ ] Changed image-processing behavior
- [ ] No detection or API changes

#### Test Images

[Describe the test images used without including private user images]

#### Checklist

- [ ] The change matches the related Jira task.
- [ ] Code follows project conventions.
- [ ] Detection results were reviewed when applicable.
- [ ] Error handling was tested when applicable.
- [ ] No user-uploaded room images were committed.
- [ ] No model weights or datasets were committed.
- [ ] No passwords, API keys, or other secrets were committed.
- [ ] No unnecessary files were committed.
- [ ] Documentation was updated when needed.
- [ ] The change is ready for review.

#### Testing Instructions

[Provide clear instructions for reviewers to test the changes]

#### Prerequisites

- [List required Python version and dependencies]
- [List required placeholder environment variables]
- [List any required local model files]
- [List any required backend service]

#### Step-by-Step Testing

1. Pull this branch.
2. Create and activate a Python virtual environment.
3. Install the project dependencies.
4. Copy `.env.example` to `.env`.
5. Start the FastAPI service.
6. Submit an approved test image.
7. Verify the response and detection results.

#### Expected Result

[Describe the expected API response or detection behavior]
