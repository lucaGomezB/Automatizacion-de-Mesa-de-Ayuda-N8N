# syntax=docker/dockerfile:1
#
# Derived N8N image for the Mesa de Ayuda email channel (change c-182).
#
# Base image (pinned, unchanged): n8nio/n8n:2.11.2
# Patched bundled package:        @n8n/imap@0.16.0 (vendored by pnpm)
#
# Root cause
#   The bundled @n8n/imap decodes `quoted-printable` parts without propagating the
#   part charset to PartData.fromData(data, encoding). The package then re-encodes
#   the latin-1 bytes as UTF-8 and the body is persisted as mojibake
#   (C3 B1 -> "Ã±"). Bodies whose lines exceed 78 bytes travel as quoted-printable
#   and are affected; 8bit/base64 parts are not.
#
# Fix
#   Pass the declared part charset as the third argument so UTF-8 quoted-printable
#   parts are decoded via `utf8.decode(qp.decode(...))`:
#       PartData.fromData(data, encoding)                      [before]
#       PartData.fromData(data, encoding, part.params?.charset) [after]
#   The change is the versioned, single-hunk patch
#   ./imap-simple-fromdata-charset.patch, applied by ./apply-unified-patch.mjs.
#
# Failure guard
#   The build is deterministic and FAILS (non-zero exit) if
#     (1) the target file does not exist, or
#     (2) the exact substitution does not apply.
#   An image can never be produced silently without the patch.
#
# Validation: docs/runbook-fix-encoding-correo-n8n.md
# Rollback:  docker-compose.yml services n8n / n8n-corpus back to `image: n8nio/n8n:2.11.2`.

FROM n8nio/n8n:2.11.2

# The n8n image runs as the unprivileged `node` user (uid 1000); the vendored
# package lives under /usr/local, so the patch step runs as root and the runtime
# user is restored afterwards.
USER root

# @n8n/imap is vendored by pnpm inside the n8n install tree. This path is pinned
# to the 2.11.2 layout and is validated before patching; a base-image bump must
# re-verify it (see the runbook).
ARG IMAP_SIMPLE_JS=/usr/local/lib/node_modules/n8n/node_modules/.pnpm/@n8n+imap@file+packages+@n8n+imap/node_modules/@n8n/imap/dist/imap-simple.js

COPY imap-simple-fromdata-charset.patch /tmp/c182-imap-simple.patch
COPY apply-unified-patch.mjs /tmp/c182-apply-unified-patch.mjs

RUN set -eux; \
    test -f "$IMAP_SIMPLE_JS" || { echo "c-182 FATAL: target file not found: $IMAP_SIMPLE_JS"; exit 1; }; \
    node /tmp/c182-apply-unified-patch.mjs "$IMAP_SIMPLE_JS" /tmp/c182-imap-simple.patch; \
    grep -qF 'PartData.fromData(data, encoding, part.params?.charset));' "$IMAP_SIMPLE_JS" || { echo "c-182 FATAL: substitution not present after patch"; exit 1; }; \
    rm -f /tmp/c182-imap-simple.patch /tmp/c182-apply-unified-patch.mjs

# Restore the base image runtime user.
USER node
