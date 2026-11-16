---
name: cloud-desktop
description: Open an app in shared Chrome, test a user flow, inspect a Linux window, capture the screen, or hand control to the user. Diagnose missing Cloud desktop tools.
---

Use the attached desktop for hands-on work in a Cloud app, even with the Desktop panel closed. “Try signup and tell me what appears after Submit” or “capture this signed-in tab” calls for the actual browser session. Use the project’s test runner for “run the signup suite.” Use headless automation for repeatable checks such as screenshots at several viewport sizes. If the result depends on a visible window or an existing session, use the browser that reproduces that condition.

For a broad request like “test signup,” choose the checks that answer the question. If the form shows an error after submission, an API or regression check can help distinguish a display problem from a failed signup. Report what each check established.

Use the browser, tab, or device the user names. If they leave the choice to you, open a Cloud app in shared Chrome at its local URL, such as `http://127.0.0.1:3000`, even when forwarding to the user’s browser is unavailable. For an external URL with no browser specified, follow the available browser tool’s selection instructions.

## Open and inspect

Use the running app if it is ready. To start it, follow the environment’s **Start skill** and its readiness check when available, or use the project’s usual command and verify it responds. When starting an app, avoid managed browser ports such as `8000` and `8085`, even if they appear free. If the app’s port conflicts, use the project’s supported port override and verify the app responds on the new port. For a UI fix, reproduce the problem when possible and repeat those steps after the change. Use the Linux desktop for native windows, file pickers, or flows that cross apps. For example, open an exported PDF to check its layout.

For the Cloud desktop, follow the first-call instructions on the desktop JavaScript tool offered for this turn (usually `cua_repl.js`). To open a new tab in shared Chrome, use `await cua.createBrowserTab("cdp", url)` when offered. To find an existing tab or app, use `await cua.getState()` and follow the tool’s tab selection or claiming instructions. Use Sky when available for a native window or a screenshot of the whole desktop. Inspect what loaded before reporting success.

If the user requests a recording, use a recorder that can capture the chosen tab or window. Keep sign-in and credentials out of the footage. Play back the saved video to verify it shows the requested steps, then link the file in this chat.

## Let the user watch or take over

When the user asks to see the app or needs to act, open the viewer with `open_in_codex({"target":{"type":"cloud-desktop"}})` if offered. In supported Codex desktop chats, the user can also choose **New tab (+) → Desktop** in the right panel. For sign-in or another handoff, have the user select **Take over** and pause your input. After they select **Return control**, inspect the same screen before continuing. Closing the panel leaves the desktop running.

## Open the app in the user’s own browser

If the user wants the running app on their computer, verify its local port on the Cloud machine. When offered, call `open_cloud_preview` with that port and return its `localUrl`. The URL works only on the user’s computer and the app handles its own login. To share with someone else, use a supported sharing or deployment route for the intended audience.

## If the desktop is unavailable

Check `capabilities[].remote_desktop` in `cloud_environment.environment_status({})` if the returned `environment_id` matches this desktop. An on-demand desktop can show `enabled: true` and `state: unknown` until first use. The first valid desktop JavaScript call or a viewer connection starts the display. Chrome can start separately when an operation needs a tab.

If the environment is starting, recheck its tools when ready. If only the viewer works, offer to open it. For a check that another browser can reproduce, try the project’s browser runner or another available browser tool and state what it verified. If the task needs the original tab, native window, or a handoff, report which interaction is blocked, the environment ID, and the missing tool or error.

If the viewer connects but Chrome fails to start, native windows may still work. If Chrome opens but a site fails to load, compare the same URL with the shell’s configured HTTP client. Report which path failed before proposing a network change.
