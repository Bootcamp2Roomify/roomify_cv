# Contributing to Roomify Computer Vision

Thank you for contributing to Roomify. All team members must follow the agreed Git and GitHub workflow.

## Branch Strategy

Roomify uses the following branches:

- `main` contains stable and reviewed code.
- `develop` contains completed development work before release.
- `feature/*` is used for new features.
- `fix/*` is used for bug fixes.
- `docs/*` is used for documentation changes.

Examples:

```text
feature/image-analysis
feature/furniture-detection
fix/image-validation
docs/cv-setup
```

## Development Workflow

1. Select or receive a Jira task.
2. Switch to the `develop` branch.
3. Make sure `develop` is up to date.
4. Create a new branch from `develop`.
5. Make and test the required changes.
6. Commit using a Conventional Commit message.
7. Push the branch to GitHub.
8. Open a Pull Request into `develop`.
9. Request a review from at least one teammate.
10. Address review comments and resolve merge conflicts.
11. Merge only after the Pull Request is approved.

Team members should not push development work directly into `main` or `develop`.

## Creating a Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/descriptive-name
```

Example:

```bash
git checkout -b feature/furniture-detection
```

## Conventional Commits

Use the following commit types:

- `feat:` for a new feature
- `fix:` for a bug fix
- `docs:` for documentation changes
- `chore:` for project setup or maintenance
- `test:` for adding or updating tests
- `refactor:` for code improvements without behavior changes

Examples:

```text
feat(detection): add furniture detection endpoint
fix(image): reject unsupported image formats
docs: update computer vision setup instructions
test(detection): add furniture detection tests
chore: configure Python gitignore
```

## Pull Request Titles

Pull Request titles must include the related Jira issue key:

```text
[ROOM-###] <type>: Brief description
```

Example:

```text
[ROOM-7] docs: Set up computer vision repository and Git workflow
```

## Pull Request Requirements

Each Pull Request must:

- Target the `develop` branch.
- Include a clear description and summary.
- Reference the related Jira task.
- Include testing instructions and expected results.
- Describe test images without committing private images.
- Be reviewed by at least one teammate.
- Resolve comments and merge conflicts before merging.
- Contain no passwords, API keys, credentials, or private data.

## Computer Vision Guidelines

Contributors should:

- Keep FastAPI routes separate from image-analysis logic.
- Use request and response schemas for API data.
- Validate image type and size before processing.
- Return safe and understandable error messages.
- Document changes to detection labels or response formats.
- Treat confidence scores as estimates rather than guarantees.
- Allow uncertain or incomplete detections to be reviewed.
- Communicate with the Roomify frontend through the Spring Boot backend.

Do not claim centimeter-perfect room measurement or guaranteed furniture dimensions from a single photograph.

## Images, Models, and Datasets

Do not commit:

- User-uploaded room images
- Private or copyrighted datasets without permission
- Generated room images
- Large model weights
- Temporary processed images
- Personal user data

Model weights and datasets should be stored in an approved external location and documented without exposing private credentials.

Use only authorized, non-sensitive test images during development and review.

## Environment Variables and Secrets

Use `.env.example` to document required environment-variable names.

Create the local environment file with:

```bash
cp .env.example .env
```

Never commit:

- Completed `.env` files
- AWS access keys
- Cloud-storage credentials
- OpenAI or Gemini API keys
- Database credentials
- JWT secrets
- Private keys or certificates

Production secrets should be stored securely using AWS Secrets Manager.

## Testing

Before submitting a Pull Request:

1. Run the FastAPI service locally.
2. Test the affected endpoint.
3. Test valid and invalid image inputs.
4. Review detection results when applicable.
5. Confirm errors do not expose credentials or internal details.
6. Confirm existing functionality still works.
7. Document the test results in the Pull Request.

## Merge Strategy

Feature, fix, and documentation branches must be merged into `develop` through Pull Requests.

```text
feature/* → develop
fix/* → develop
docs/* → develop
```

The `develop` branch should only be merged into `main` when the service is stable and ready for release.
