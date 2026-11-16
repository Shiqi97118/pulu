---
name: cloud-environment-runtime
description: Use when a task needs guidance on a managed Codex Cloud computer’s workspace, available tools, setup, or network access.
---

The selected Cloud environment is your computer for this task. Use its workspace, shell, installed applications, and configured connections to do the work and verify the result.

When you start or resume work on the Cloud computer, call `cloud_environment.environment_status({})` if available. Check again after its configuration changes. Its `environment_id` identifies the machine it describes. If status is unavailable or describes a different machine, continue with what you can verify on the selected computer. Discard earlier status when the machine changes or detaches.

- **Work with files or code.** Each task has its own workspace. A Default environment can start without a repository. On resume, inspect the files already there and preserve existing edits. For repo work, use the matching checkout or connected provider. Read [Repositories](references/repositories.md) to verify a requested revision, find a missing checkout, or resolve a provider access issue.
- **Inspect what the user sees.** Use this plugin’s `cloud-desktop` skill to explore a running Cloud app, investigate a visual bug interactively, use an existing browser session or native window, or hand control to the user. Honor any browser, tab, device, or test mode the user names.
- **Run a suite or repeat a check.** Use the project’s test command and its configured browser mode. For new scripted checks, prefer headless automation such as Playwright for repeatable assertions, viewport sweeps, and scripted captures. Use a visible browser when the check depends on a real display. If a scripted check fails, reproduce the failing step in the app when it would help explain the failure.
- **Deliver a file.** Open or read back the result in its intended format and link its absolute path in the originating chat. On supported desktop clients, **Save as…** downloads a copy.
- **Set up tools.** Read [Packages](references/packages.md) before installing dependencies or [Docker](references/docker.md) before building or running containers.
- **Connect to a service.** Read [Networking](references/networking.md) to check current policy and credentials, then test the intended service with its actual client. For a configured VPN or a private connectivity problem, also read [VPN](references/vpn.md).
- **Change or repair the environment.** Read [Environment changes](references/environment-changes.md) for onboarding, adding repositories to the configuration, or changing access. Read [Diagnostics](references/diagnostics.md) before inspecting setup logs.
