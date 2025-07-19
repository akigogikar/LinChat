# Team Workspaces

This document outlines the requirements for supporting collaborative workspaces in LinChat. It covers creation of workspaces, how members are managed and how documents or chat threads can be shared or kept private. In addition, it specifies how audit logs must record both personal and workspace level activity.

## Workspace Creation

- Any authenticated user may create a workspace.
- Each workspace must have a unique name.
- The creator becomes the initial workspace admin.
- A user can belong to multiple workspaces and can switch between them in the UI.

## Membership Management

- Workspace admins can invite new members by username or email.
- Invited users receive a notification and must accept before being added.
- Admins can promote members to admin or remove them from the workspace.
- Membership changes (invitations, role updates, removals) are recorded in the audit log.

## Shared vs. Private Documents and Chats

- Uploaded documents are private to the owner by default.
- Owners can mark a document as shared with one of their workspaces.
- Shared documents are readable by all members of that workspace.
- Chat threads follow the same rule: they are private unless explicitly shared with a workspace.
- Moving a private document or chat into a workspace, or changing a shared item back to private, generates an audit log entry.

## Audit Log Requirements

- Every log entry must record the acting user and a timestamp.
- Actions performed within a workspace include the workspace ID in the log entry.
- Personal actions (such as managing a private document) store `null` for the workspace field.
- The admin interface should allow filtering the audit log by workspace or by individual user.
- Example actions to log include:
  - creating or deleting a workspace
  - adding or removing members
  - uploading, sharing or deleting documents
  - starting or sharing chat threads

